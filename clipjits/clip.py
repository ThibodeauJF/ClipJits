"""Clip management and MPV integration."""

import json
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import click

from .config import config
from .utils import sanitize_filename, format_timestamp, parse_timestamp


class ClipQueue:
    """Manage the queue of video clips to be extracted."""

    def __init__(self, queue_file: Optional[Path] = None):
        self.queue_file = queue_file or config.clip_queue_file
        self.clips: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        """Load clip queue from JSON file."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clips = data.get('clips', [])
            except Exception as e:
                click.echo(f"Warning: Could not load queue file: {e}", err=True)
                self.clips = []
        else:
            self.clips = []

    def save(self):
        """Save clip queue to JSON file."""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump({'clips': self.clips}, f, indent=2)

    def add_clip(
        self,
        source_video: Path,
        start_time: str,
        end_time: str,
        label: Optional[str] = None
    ) -> str:
        """Add a clip to the queue."""
        clip_id = str(uuid.uuid4())
        clip = {
            'id': clip_id,
            'source_video': str(source_video.absolute()),
            'start_time': start_time,
            'end_time': end_time,
            'label': label or '',
            'created_at': datetime.now().isoformat()
        }
        self.clips.append(clip)
        self.save()
        return clip_id

    def list_clips(self) -> List[Dict[str, Any]]:
        """Get list of all clips in queue."""
        return self.clips

    def remove_clip(self, clip_id: str) -> bool:
        """Remove a clip from the queue by ID."""
        original_length = len(self.clips)
        self.clips = [c for c in self.clips if c['id'] != clip_id]
        if len(self.clips) < original_length:
            self.save()
            return True
        return False

    def clear(self):
        """Clear all clips from the queue."""
        self.clips = []
        self.save()

    def update_clip_label(self, clip_id: str, new_label: str) -> bool:
        """Update the label of a clip."""
        for clip in self.clips:
            if clip['id'] == clip_id:
                clip['label'] = new_label
                self.save()
                return True
        return False


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
        cmd = [
            'mpv',
            f'--script={script_path}',
            f'--script-opts=clipjits-queue-file={config.clip_queue_file}',
            str(video_path)
        ]
    
    click.echo(f"Launching MPV for: {video_path}")
    click.echo("\nKeybindings:")
    click.echo("  s - Mark clip start")
    click.echo("  e - Mark clip end")
    click.echo("  c - Commit clip to queue (prompts for label)")
    click.echo("  q - Quit MPV\n")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"MPV failed: {e}")
    except FileNotFoundError:
        raise click.ClickException(
            "MPV not found. Please install MPV media player."
        )


def extract_clips(output_dir: Optional[Path] = None, queue: Optional[ClipQueue] = None):
    """Extract all clips from the queue using ffmpeg."""
    queue = queue or ClipQueue()
    output_dir = output_dir or config.clips_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    clips = queue.list_clips()
    
    if not clips:
        click.echo("No clips in queue to extract.")
        return
    
    click.echo(f"Extracting {len(clips)} clips to {output_dir}...")
    
    for i, clip in enumerate(clips, 1):
        source_video = Path(clip['source_video'])
        
        if not source_video.exists():
            click.echo(f"[{i}/{len(clips)}] Skipping - source video not found: {source_video}", err=True)
            continue
        
        source_name = sanitize_filename(source_video.stem)
        label = sanitize_filename(clip['label']) if clip['label'] else f"clip{i}"
        
        output_filename = f"{source_name}_{label}.mp4"
        output_path = output_dir / output_filename
        
        start_seconds = parse_timestamp(clip['start_time'])
        end_seconds = parse_timestamp(clip['end_time'])
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
        
        click.echo(f"[{i}/{len(clips)}] Extracting: {output_filename}")
        
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            click.echo(f"  Saved to: {output_path}")
        except subprocess.CalledProcessError as e:
            click.echo(f"  Failed: {e.stderr}", err=True)
    
    click.echo(f"\nExtraction complete. {len(clips)} clips processed.")
