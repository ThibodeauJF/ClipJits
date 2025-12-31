"""Batch processing of clips with transcription and LLM summarization."""

import shutil
from pathlib import Path
from typing import Optional, List, Dict
from collections import defaultdict
import click

from .config import config
from .utils import to_snake_case


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
    transcripts: List[str],
    video_filenames: List[str],
    provider: str = "openai",
    model: Optional[str] = None
) -> tuple[str, str]:
    """
    Generate technique summary using LLM.
    
    Args:
        transcripts: List of video transcripts
        video_filenames: List of video filenames for reference
        provider: LLM provider (openai/anthropic)
        model: Model name
    
    Returns:
        Tuple of (technique_name, markdown_content)
    """
    combined_transcript = "\n\n---\n\n".join(
        [f"Clip {i+1}:\n{t}" for i, t in enumerate(transcripts)]
    )
    
    prompt = f"""You are analyzing a BJJ instructional video transcript. Your job is to extract ONLY what is actually said in the transcript.

TRANSCRIPT:
{combined_transcript}

CRITICAL RULES - READ CAREFULLY:
1. If the transcript is empty, contains only gibberish, or has no actual English words discussing BJJ techniques, you MUST output ONLY:
   - A generic technique name based on the filename
   - The video embeds
   - NOTHING ELSE. NO steps, NO descriptions, NO made-up content.

2. If there IS actual speech about BJJ techniques in the transcript:
   - Extract a technique name for the title
   - Write ONLY the steps and details that are explicitly mentioned in the transcript
   - Remove filler words, repetitions, and verbal artifacts
   - Remove nonsensical text, non-English words, and transcribed background sounds
   - Use direct technical language only
   - NO introductions, meta-commentary, safety disclaimers, or conclusions

3. ABSOLUTELY FORBIDDEN:
   - DO NOT invent steps that aren't in the transcript
   - DO NOT add generic BJJ knowledge
   - DO NOT make assumptions about what the technique might be
   - DO NOT write anything that isn't directly stated in the transcript
   - If you can't extract real content, output ONLY the title and video embeds

At the end, add the video embeds with blank lines between them:

{chr(10).join([f'![[{fn}]]' for fn in video_filenames])}

Remember: An empty output with just the title and video embeds is BETTER than making up content that isn't in the transcript."""

    if provider == "openai":
        content = _generate_with_openai(prompt, model)
    elif provider == "anthropic":
        content = _generate_with_anthropic(prompt, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    # Extract technique name from the markdown
    lines = content.strip().split('\n')
    technique_name = None
    title_line = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith('# '):
            technique_name = line_stripped[2:].strip()
            title_line = i
            break
        # Handle bold format: **Title**
        elif line_stripped.startswith('**') and line_stripped.endswith('**') and len(line_stripped) > 4:
            technique_name = line_stripped[2:-2].strip()
            title_line = i
            break
    
    # If no title found, use first non-empty line
    if not technique_name:
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped:
                technique_name = line_stripped.replace('#', '').replace('*', '').strip()
                title_line = i
                break
    
    # Last resort fallback
    if not technique_name:
        technique_name = "untitled_technique"
    
    # Remove the title line from content
    if title_line is not None:
        lines.pop(title_line)
        # Remove any empty lines right after the title
        while title_line < len(lines) and not lines[title_line].strip():
            lines.pop(title_line)
        content = '\n'.join(lines).strip()
    
    return technique_name, content


def _generate_with_openai(prompt: str, model: Optional[str] = None) -> str:
    """Generate summary using OpenAI API."""
    from openai import OpenAI
    
    client = OpenAI(api_key=config.openai_api_key)
    model = model or config.llm_model
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a BJJ technique documenter. You ONLY document what is explicitly stated in transcripts. You NEVER invent, assume, or add information. If a transcript has no real content, you output only a title and video embeds with no description."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
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
        system="You are a BJJ technique documenter. Output only factual technique descriptions with no fluff.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text


def group_clips_by_label(clips_dir: Path) -> Dict[str, List[Path]]:
    """
    Group clips by their label, combining labels with numeric suffixes.
    Examples: "arm drag 1.mp4", "arm drag 2.mp4" -> grouped as "arm drag"
              "arm bar1.mp4", "arm bar2.mp4" -> grouped as "arm bar"
              "kimura.mp4" -> grouped as "kimura"
              "arm_drag_1.mp4" -> grouped as "arm_drag"
    
    Returns dict with base labels as keys and lists of clip paths as values.
    """
    import re
    groups = defaultdict(list)
    
    for video_path in sorted(clips_dir.glob("*.mp4")):
        filename = video_path.stem
        
        # Remove trailing numeric suffix (with optional space or underscore before it)
        # Matches: "label 1", "label_1", "label1"
        base_label = re.sub(r'[\s_]?\d+$', '', filename).strip()
        
        # If removing the number left us with nothing, use original
        if not base_label:
            base_label = filename
        
        groups[base_label].append(video_path)
    
    return dict(groups)


def process_clips(
    whisper_model: Optional[str] = None,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    skip_transcription: bool = False,
    resume: bool = False
):
    """
    Process video clips: transcribe and generate technique summaries.
    
    Clips are read from vault/clips/, processed, and moved to vault/clips/processed/.
    Media files are copied to vault/Media/ and markdown is saved to vault/Techniques/.
    
    Args:
        whisper_model: Whisper model size
        llm_provider: LLM provider
        llm_model: LLM model name
        skip_transcription: Use existing transcript files
        resume: Skip already processed clips
    """
    clips_dir = config.clips_dir
    processed_dir = config.clips_processed_dir
    media_dir = config.media_dir
    techniques_dir = config.techniques_dir
    
    # Ensure directories exist
    clips_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    techniques_dir.mkdir(parents=True, exist_ok=True)
    
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
        click.echo("No video clips found in clips directory.")
        return
    
    total_groups = len(grouped_clips)
    click.echo(f"Found {total_groups} technique(s) to process.\n")
    
    for group_idx, (label_name, video_paths) in enumerate(sorted(grouped_clips.items()), 1):
        click.echo(f"[{group_idx}/{total_groups}] Processing: {label_name}")
        click.echo(f"  Clips in group: {len(video_paths)}")
        
        transcripts = []
        
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
        
        if not transcripts:
            click.echo(f"  No transcripts available, skipping group.")
            continue
        
        click.echo(f"  Generating technique summary with {llm_provider}...")
        
        try:
            # Generate with original filenames for embedding
            original_filenames = [p.name for p in video_paths]
            technique_name, summary = generate_technique_summary(
                transcripts,
                original_filenames,
                llm_provider,
                llm_model
            )
            
            # Convert technique name to snake_case for filename
            technique_filename = to_snake_case(technique_name)
            
            # Copy media files to Media/ with numbered suffix
            media_filenames = []
            for idx, video_path in enumerate(video_paths, 1):
                media_filename = f"{technique_filename}_{idx}.mp4"
                media_path = media_dir / media_filename
                shutil.copy2(video_path, media_path)
                media_filenames.append(media_filename)
                click.echo(f"  Copied to media: {media_filename}")
            
            # Update markdown to reference new media filenames with spacing
            for original, new in zip(original_filenames, media_filenames):
                summary = summary.replace(f"![[{original}]]", f"![[{new}]]")
            
            # Save markdown to Techniques/ (convert snake_case to Title Case)
            technique_readable = technique_filename.replace('_', ' ').title()
            output_file = techniques_dir / f"{technique_readable}.md"
            
            if resume and output_file.exists():
                click.echo(f"  Skipping - already processed: {output_file.name}")
                continue
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            click.echo(f"  Saved technique: {output_file.name}")
            
            # Move processed clips to processed/ directory
            for video_path in video_paths:
                processed_path = processed_dir / video_path.name
                shutil.move(str(video_path), str(processed_path))
                
                # Also move transcript files if they exist
                transcript_file = video_path.with_suffix('.txt')
                if transcript_file.exists():
                    processed_transcript = processed_dir / transcript_file.name
                    shutil.move(str(transcript_file), str(processed_transcript))
            
            click.echo(f"  Moved {len(video_paths)} clip(s) to processed/\n")
            
        except Exception as e:
            click.echo(f"  Processing failed: {e}", err=True)
            continue
    
    click.echo(f"Processing complete. Processed {total_groups} technique(s).")

