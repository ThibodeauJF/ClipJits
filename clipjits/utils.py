"""Utility functions for ClipJits."""

import re
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing special characters."""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename.strip('_')


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def parse_timestamp(timestamp: str) -> float:
    """Parse timestamp string (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    else:
        return float(timestamp)


def get_video_duration(video_path: Path) -> Optional[float]:
    """Get video duration in seconds using ffprobe."""
    import subprocess
    import json
    
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(video_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception:
        return None


def extract_base_label(label: str) -> tuple[str, Optional[int]]:
    """Extract base label and number from labels like 'armbar1', 'armbar2'."""
    match = re.match(r'^(.+?)(\d+)$', label)
    if match:
        return match.group(1), int(match.group(2))
    return label, None
