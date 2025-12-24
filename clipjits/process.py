"""Batch processing of clips with transcription and LLM summarization."""

import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from collections import defaultdict
import click

from .config import config
from .utils import extract_base_label


def transcribe_video(video_path: Path, model_size: str = "base") -> str:
    """
    Transcribe video audio using OpenAI Whisper.
    
    Args:
        video_path: Path to video file
        model_size: Whisper model size (tiny/base/small/medium/large)
    
    Returns:
        Transcribed text
    """
    import whisper
    
    click.echo(f"  Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    
    click.echo(f"  Transcribing audio...")
    result = model.transcribe(str(video_path))
    
    return result['text'].strip()


def generate_technique_summary(
    transcript: str,
    video_filename: str,
    provider: str = "openai",
    model: Optional[str] = None
) -> str:
    """
    Generate technique summary using LLM.
    
    Args:
        transcript: Video transcript
        video_filename: Name of the video file
        provider: LLM provider (openai/anthropic)
        model: Model name
    
    Returns:
        Markdown formatted technique summary
    """
    prompt = f"""You are analyzing a Brazilian Jiu Jitsu instructional video clip. The instructor describes the following technique:

{transcript}

Generate a comprehensive technique card with:
1. Technique name and category
2. Step-by-step breakdown (numbered list)
3. Various concepts and details concerning the technique

Format as markdown suitable for Obsidian. Include the video embed at the end using: ![[{video_filename}]]"""

    if provider == "openai":
        return _generate_with_openai(prompt, model)
    elif provider == "anthropic":
        return _generate_with_anthropic(prompt, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def _generate_with_openai(prompt: str, model: Optional[str] = None) -> str:
    """Generate summary using OpenAI API."""
    from openai import OpenAI
    
    client = OpenAI(api_key=config.openai_api_key)
    model = model or config.llm_model
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a Brazilian Jiu Jitsu instructor creating detailed technique cards."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    
    return response.choices[0].message.content


def _generate_with_anthropic(prompt: str, model: Optional[str] = None) -> str:
    """Generate summary using Anthropic API."""
    from anthropic import Anthropic
    
    client = Anthropic(api_key=config.anthropic_api_key)
    model = model or "claude-3-5-sonnet-20241022"
    
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system="You are a Brazilian Jiu Jitsu instructor creating detailed technique cards.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text


def group_clips_by_label(clips_dir: Path) -> Dict[str, List[Path]]:
    """Group video clips by their base label (e.g., armbar1, armbar2 -> armbar)."""
    groups = defaultdict(list)
    
    for video_path in sorted(clips_dir.glob("*.mp4")):
        filename = video_path.stem
        
        parts = filename.rsplit('_', 1)
        if len(parts) == 2:
            label = parts[1]
        else:
            label = filename
        
        base_label, number = extract_base_label(label)
        
        groups[base_label].append(video_path)
    
    return dict(groups)


def combine_transcripts(transcripts: List[str]) -> str:
    """Combine multiple transcripts with clear separation."""
    combined = []
    for i, transcript in enumerate(transcripts, 1):
        combined.append(f"Clip {i}:\n{transcript}")
    return "\n\n---\n\n".join(combined)


def process_clips(
    clips_dir: Path,
    output_dir: Optional[Path] = None,
    whisper_model: Optional[str] = None,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    skip_transcription: bool = False,
    resume: bool = False
):
    """
    Process video clips: transcribe and generate technique summaries.
    
    Args:
        clips_dir: Directory containing video clips
        output_dir: Output directory for markdown files
        whisper_model: Whisper model size
        llm_provider: LLM provider
        llm_model: LLM model name
        skip_transcription: Use existing transcript files
        resume: Skip already processed clips
    """
    output_dir = output_dir or config.obsidian_vault_path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    whisper_model = whisper_model or config.whisper_model_size
    llm_provider = llm_provider or config.llm_provider
    llm_model = llm_model or config.llm_model
    
    if not config.validate_api_keys():
        raise click.ClickException(
            f"API key not configured for provider: {llm_provider}. "
            "Please set the appropriate API key in your .env file."
        )
    
    if not clips_dir.exists():
        raise click.ClickException(f"Clips directory not found: {clips_dir}")
    
    grouped_clips = group_clips_by_label(clips_dir)
    
    if not grouped_clips:
        click.echo("No video clips found in directory.")
        return
    
    total_groups = len(grouped_clips)
    click.echo(f"Found {total_groups} technique groups to process.\n")
    
    for group_idx, (base_label, video_paths) in enumerate(sorted(grouped_clips.items()), 1):
        click.echo(f"[{group_idx}/{total_groups}] Processing technique: {base_label}")
        click.echo(f"  Clips in group: {len(video_paths)}")
        
        output_file = output_dir / f"{base_label}.md"
        
        if resume and output_file.exists():
            click.echo(f"  Skipping - already processed")
            continue
        
        transcripts = []
        video_filenames = []
        
        for video_path in video_paths:
            transcript_file = video_path.with_suffix('.txt')
            
            if skip_transcription and transcript_file.exists():
                click.echo(f"  Using existing transcript: {transcript_file.name}")
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript = f.read().strip()
            else:
                try:
                    transcript = transcribe_video(video_path, whisper_model)
                    
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    
                except Exception as e:
                    click.echo(f"  Transcription failed: {e}", err=True)
                    continue
            
            transcripts.append(transcript)
            video_filenames.append(video_path.name)
        
        if not transcripts:
            click.echo(f"  No transcripts available, skipping group.")
            continue
        
        combined_transcript = combine_transcripts(transcripts)
        
        click.echo(f"  Generating technique summary with {llm_provider}...")
        
        try:
            video_embeds = "\n".join([f"![[{fn}]]" for fn in video_filenames])
            summary = generate_technique_summary(
                combined_transcript,
                video_embeds,
                llm_provider,
                llm_model
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            click.echo(f"  Saved to: {output_file}\n")
            
        except Exception as e:
            click.echo(f"  LLM generation failed: {e}", err=True)
            continue
    
    click.echo(f"Processing complete. Processed {total_groups} technique groups.")
