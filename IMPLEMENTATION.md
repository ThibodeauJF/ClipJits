# ClipJits Implementation

## Overview
CLI tool for creating BJJ technique cards from instructional videos with immediate clip extraction and AI-powered processing.

## Architecture

### Core Components

- **config.py** - Environment-based configuration with vault structure
- **download.py** - Video downloader using yt-dlp
- **clip.py** - MPV integration and FFmpeg clip extraction
- **process.py** - Whisper transcription + LLM summarization
- **cli.py** - Click-based command interface
- **utils.py** - Snake_case conversion and timestamp parsing

### MPV Lua Script
- `mpv-scripts/clip-marker.lua` - Keyboard shortcuts (s/e/c) with immediate FFmpeg extraction

## Vault Structure
```
jits/
  clips/              # Active clips ready to process
  clips/processed/    # Processed clips (archived)
  downloads/          # Downloaded videos
  Techniques/         # Generated markdown files
  Media/              # Media files referenced in markdown
```

## Workflow

1. **Download**: `clipjits download <url>` → saves to `jits/downloads/`
2. **Watch**: `clipjits watch <video>` → press s/e/c → clips extract to `jits/clips/`
3. **Process**: `clipjits process` → transcribes, generates markdown, moves to processed/

## Key Features

- Immediate clip extraction (no queue)
- Required label input
- Snake_case filenames (50 char limit)
- Automatic clip grouping by source video
- Multi-provider LLM support (OpenAI, Anthropic)
- Multiple Whisper model sizes
- Obsidian-compatible markdown output

## Technology Stack

- Python 3.10+, Click, yt-dlp, FFmpeg, MPV, Whisper, OpenAI/Anthropic APIs
