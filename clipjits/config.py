"""Configuration management for ClipJits."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for ClipJits."""

    def __init__(self):
        self.source_videos_dir = Path(
            os.getenv("SOURCE_VIDEOS_DIR", "./source-videos")
        ).expanduser()
        self.clips_output_dir = Path(
            os.getenv("CLIPS_OUTPUT_DIR", "./clips")
        ).expanduser()
        self.obsidian_vault_path = Path(
            os.getenv("OBSIDIAN_VAULT_PATH", "~/Documents/ObsidianVault/BJJ/techniques")
        ).expanduser()

        self.default_video_quality = os.getenv("DEFAULT_VIDEO_QUALITY", "1080p")

        self.whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "base")

        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.ffmpeg_video_codec = os.getenv("FFMPEG_VIDEO_CODEC", "libx264")
        self.ffmpeg_audio_codec = os.getenv("FFMPEG_AUDIO_CODEC", "aac")

        self.clip_name_template = os.getenv("CLIP_NAME_TEMPLATE", "{source}_{label}")
        
        self.mpv_ipc_socket = os.getenv("MPV_IPC_SOCKET", "/tmp/mpv-socket")
        
        self.clip_queue_file = Path.home() / ".clipjits" / "clip_queue.json"

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.source_videos_dir.mkdir(parents=True, exist_ok=True)
        self.clips_output_dir.mkdir(parents=True, exist_ok=True)
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        self.clip_queue_file.parent.mkdir(parents=True, exist_ok=True)

    def validate_api_keys(self) -> bool:
        """Validate that appropriate API keys are set."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            return False
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            return False
        return True


config = Config()
