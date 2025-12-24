"""Video download functionality using yt-dlp."""

import subprocess
from pathlib import Path
from typing import Optional
import click

from .config import config
from .utils import sanitize_filename


def download_video(
    url: str,
    quality: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Download video from URL using yt-dlp.
    
    Args:
        url: Video URL (YouTube, Instagram, Reddit, X)
        quality: Video quality (e.g., '1080p', '720p')
        output_dir: Output directory for downloaded video
    
    Returns:
        Path to downloaded video file
    """
    quality = quality or config.default_video_quality
    output_dir = output_dir or config.source_videos_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    height = quality.replace('p', '')
    
    output_template = str(output_dir / '%(title)s.%(ext)s')
    
    cmd = [
        'yt-dlp',
        '-f', f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        '--merge-output-format', 'mp4',
        '-o', output_template,
        '--progress',
        '--newline',
        url
    ]
    
    click.echo(f"Downloading video from {url}...")
    click.echo(f"Quality: {quality}")
    click.echo(f"Output directory: {output_dir}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        
        result_cmd = subprocess.run(
            ['yt-dlp', '--get-filename', '-o', output_template, url],
            capture_output=True,
            text=True,
            check=True
        )
        
        output_path = Path(result_cmd.stdout.strip())
        
        click.echo(f"\nDownload complete: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Download failed: {e}")
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")
