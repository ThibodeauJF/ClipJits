"""Command-line interface for ClipJits."""

from pathlib import Path
from typing import Optional
import click

from . import __version__
from .config import config
from .download import download_video
from .clip import launch_mpv
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
    """Download video from URL to vault/downloads/ folder."""
    try:
        download_video(url, quality)
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument('video_path', type=click.Path(exists=True, path_type=Path))
def watch(video_path: Path):
    """
    Launch MPV with clip marking enabled.
    
    Press 's' to mark start, 'e' to mark end, 'c' to commit and extract clip.
    Clips are automatically saved to vault/clips/ folder.
    """
    try:
        launch_mpv(video_path)
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
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
    model: Optional[str],
    llm_provider: Optional[str],
    llm_model: Optional[str],
    skip_transcription: bool,
    resume: bool
):
    """
    Process clips from vault/clips/ folder.
    
    Transcribes audio, generates technique summaries with LLM.
    Moves processed clips to vault/clips/processed/.
    Saves media to vault/Media/ and markdown to vault/Techniques/.
    """
    try:
        process_clips(
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
