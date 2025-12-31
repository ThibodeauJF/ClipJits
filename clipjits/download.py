import subprocess
from pathlib import Path
from typing import Optional
import click

from .config import config

def download_video(
    url: str,
    quality: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Path:
    quality = quality or config.default_video_quality
    output_dir = output_dir or config.downloads_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    height = quality.replace('p', '')
    output_template = str(output_dir / '%(title)s.%(ext)s')
    
    cmd = [
        'yt-dlp',
        '-f', f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
        '--merge-output-format', 'mp4',
        '--restrict-filenames',
        '-o', output_template,
        '--quiet',
        url
    ]
    
    try:
        click.echo("\nDownloading...")
        subprocess.run(cmd, check=True)
        click.echo("\nDownload complete, saved to: " + str(output_dir))
        return output_dir
        
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Download failed: {e}")
