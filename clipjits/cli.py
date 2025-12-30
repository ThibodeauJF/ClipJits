"""Command-line interface for ClipJits."""

from pathlib import Path
from typing import Optional
import click

from . import __version__
from .config import config
from .download import download_video
from .clip import ClipQueue, launch_mpv, extract_clips
from .process import process_clips


@click.group()
@click.version_option(version=__version__)
def cli():
    """ClipJits - Create BJJ technique cards from video clips."""
    config.ensure_directories()


@cli.command()
@click.argument('url')
@click.option('--quality', default=None, help='Video quality (e.g., 1080p, 720p)')
def download(url: str, quality: Optional[str]):
    """Download video from URL (YouTube, Instagram, Reddit, X)."""
    try:
        output_path = download_video(url, quality)
        click.echo(f"\nVideo saved to: {output_path}")
        click.echo(f"\nTo watch and clip: clipjits watch \"{output_path}\"")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('video_path', type=click.Path(exists=True, path_type=Path))
def watch(video_path: Path):
    """Launch MPV with clip marking enabled."""
    try:
        launch_mpv(video_path)
    except Exception as e:
        raise click.ClickException(str(e))


@cli.group()
def queue():
    """Manage clip queue."""
    pass


@queue.command('list')
def queue_list():
    """List all clips in the queue."""
    clip_queue = ClipQueue()
    clips = clip_queue.list_clips()
    
    if not clips:
        click.echo("Queue is empty.")
        return
    
    click.echo(f"Clip Queue ({len(clips)} clips):\n")
    
    for i, clip in enumerate(clips, 1):
        source = Path(clip['source_video']).name
        label = clip['label'] or '(no label)'
        click.echo(f"{i}. {label}")
        click.echo(f"   Source: {source}")
        click.echo(f"   Time: {clip['start_time']} -> {clip['end_time']}")
        click.echo(f"   ID: {clip['id']}")
        click.echo()


@queue.command('edit')
def queue_edit():
    """Edit clip queue (remove clips or update labels)."""
    clip_queue = ClipQueue()
    clips = clip_queue.list_clips()
    
    if not clips:
        click.echo("Queue is empty.")
        return
    
    while True:
        click.echo(f"\nClip Queue ({len(clip_queue.list_clips())} clips):\n")
        
        current_clips = clip_queue.list_clips()
        if not current_clips:
            click.echo("Queue is now empty.")
            break
        
        for i, clip in enumerate(current_clips, 1):
            label = clip['label'] or '(no label)'
            source = Path(clip['source_video']).name
            click.echo(f"{i}. {label} - {source}")
        
        click.echo("\nOptions:")
        click.echo("  [number] - Select clip to edit")
        click.echo("  [q] - Quit")
        
        choice = click.prompt("\nChoice", type=str, default='q')
        
        if choice.lower() == 'q':
            break
        
        try:
            clip_idx = int(choice) - 1
            if clip_idx < 0 or clip_idx >= len(current_clips):
                click.echo("Invalid clip number.")
                continue
            
            selected_clip = current_clips[clip_idx]
            click.echo(f"\nSelected: {selected_clip['label'] or '(no label)'}")
            click.echo("Actions:")
            click.echo("  [r] - Remove clip")
            click.echo("  [l] - Update label")
            click.echo("  [c] - Cancel")
            
            action = click.prompt("Action", type=str, default='c')
            
            if action.lower() == 'r':
                clip_queue.remove_clip(selected_clip['id'])
                click.echo("Clip removed.")
            elif action.lower() == 'l':
                new_label = click.prompt("New label", default=selected_clip['label'])
                clip_queue.update_clip_label(selected_clip['id'], new_label)
                click.echo("Label updated.")
            
        except ValueError:
            click.echo("Invalid input.")


@queue.command('clear')
@click.confirmation_option(prompt='Are you sure you want to clear the entire queue?')
def queue_clear():
    """Clear all clips from the queue."""
    clip_queue = ClipQueue()
    clip_queue.clear()
    click.echo("Queue cleared.")


@cli.command()
@click.option('--output-dir', type=click.Path(path_type=Path), default=None,
              help='Output directory for clips')
def extract(output_dir: Optional[Path]):
    """Extract all queued clips using ffmpeg."""
    try:
        extract_clips(output_dir)
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('clips_dir', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', type=click.Path(path_type=Path), default=None,
              help='Output directory for markdown files')
@click.option('--model', default=None,
              help='Whisper model size (tiny/base/small/medium/large)')
@click.option('--llm-provider', default=None,
              help='LLM provider (openai/anthropic)')
@click.option('--llm-model', default=None,
              help='LLM model name')
@click.option('--skip-transcription', is_flag=True,
              help='Use existing transcript files')
@click.option('--resume', is_flag=True,
              help='Skip already processed clips')
def process(
    clips_dir: Path,
    output_dir: Optional[Path],
    model: Optional[str],
    llm_provider: Optional[str],
    llm_model: Optional[str],
    skip_transcription: bool,
    resume: bool
):
    """Process clips: transcribe and generate technique summaries."""
    try:
        process_clips(
            clips_dir,
            output_dir,
            model,
            llm_provider,
            llm_model,
            skip_transcription,
            resume
        )
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()