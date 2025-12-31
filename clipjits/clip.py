"""Clip management and MPV integration."""

import subprocess
from pathlib import Path
import click

from .config import config
from .utils import to_snake_case, parse_timestamp


def extract_single_clip(
    source_video: Path,
    start_time: str,
    end_time: str,
    label: str,
    output_dir: Path
) -> Path:
    """
    Extract a single clip using ffmpeg.
    
    Args:
        source_video: Path to source video file
        start_time: Start timestamp (HH:MM:SS.mmm)
        end_time: End timestamp (HH:MM:SS.mmm)
        label: Clip label
        output_dir: Output directory for clip
    
    Returns:
        Path to extracted clip
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert source name to snake_case
    source_name = to_snake_case(source_video.stem)
    label_snake = to_snake_case(label)
    
    output_filename = f"{source_name}_{label_snake}.mp4"
    output_path = output_dir / output_filename
    
    start_seconds = parse_timestamp(start_time)
    end_seconds = parse_timestamp(end_time)
    duration = end_seconds - start_seconds
    
    cmd = [
        'ffmpeg',
        '-y',
        '-ss', str(start_seconds),
        '-i', str(source_video),
        '-t', str(duration),
        '-c:v', config.ffmpeg_video_codec,
        '-c:a', config.ffmpeg_audio_codec,
        '-avoid_negative_ts', 'make_zero',
        str(output_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"FFmpeg extraction failed: {e.stderr}")


def launch_mpv(video_path: Path):
    """Launch MPV with clipping script enabled."""
    if not video_path.exists():
        raise click.ClickException(f"Video file not found: {video_path}")
    
    script_path = Path(__file__).parent.parent / "mpv-scripts" / "clip-marker.lua"
    
    if not script_path.exists():
        click.echo(
            f"Warning: MPV script not found at {script_path}. "
            "MPV will launch without clipping functionality.",
            err=True
        )
        cmd = ['mpv', str(video_path)]
    else:
        # Pass configuration to Lua script
        clips_dir = config.clips_dir
        cmd = [
            'mpv',
            '--msg-level=all=no,clipjits=info',
            '--term-status-msg=',
            f'--script={script_path}',
            f'--script-opts=clipjits-clips-dir={clips_dir}',
            str(video_path)
        ]
    
    click.echo(f"Launching MPV for: {video_path}")
    click.echo("\nKeybindings:")
    click.echo("  s - Mark clip start")
    click.echo("  e - Mark clip end")
    click.echo("  c - Commit clip (prompts for label, extracts immediately)")
    click.echo("  q - Quit MPV\n")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"MPV failed: {e}")
    except FileNotFoundError:
        raise click.ClickException(
            "MPV not found. Please install MPV media player."
        )

