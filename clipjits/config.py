"""Configuration management for ClipJits."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for ClipJits."""

    def __init__(self):
        # Main vault path - all project data is stored here
        self.vault_path = Path(
            os.getenv("VAULT_PATH", "~/Jits")
        ).expanduser()
        
        # Clips subdirectory within vault
        self.clip_sub_dir = os.getenv("CLIP_SUB_DIR", "ClipJits")
        
        # Subfolder structure within vault
        clip_base = self.vault_path / self.clip_sub_dir
        self.clips_dir = clip_base / "raw-clips"
        self.clips_processed_dir = clip_base / "processed-clips"
        self.downloads_dir = clip_base / "downloads"
        self.techniques_dir = self.vault_path / "Techniques"
        self.media_dir = self.vault_path / "Media"

        self.default_video_quality = os.getenv("DEFAULT_VIDEO_QUALITY", "1080p")

        self.whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "base")

        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.ffmpeg_video_codec = os.getenv("FFMPEG_VIDEO_CODEC", "libx264")
        self.ffmpeg_audio_codec = os.getenv("FFMPEG_AUDIO_CODEC", "aac")

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.clips_processed_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.techniques_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def validate_api_keys(self) -> bool:
        """Validate that appropriate API keys are set."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            return False
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            return False
        return True


config = Config()
