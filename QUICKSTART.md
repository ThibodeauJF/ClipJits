# Quick Start

## Setup

```bash
pip install -e .
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

Install system dependencies:
```bash
winget install ffmpeg mpv  # Windows
brew install ffmpeg mpv    # macOS
```

## Commands

```bash
clipjits download "https://youtube.com/watch?v=..."
clipjits watch jits/downloads/video.mp4
clipjits process
```

If `clipjits` not found, use `python -m clipjits` instead.

## MPV Controls

- `s` - Mark start
- `e` - Mark end  
- `c` - Commit (enter label in terminal, extracts immediately)
- `q` - Quit

## Workflow

1. **Download** → `jits/downloads/`
2. **Watch** → mark clips → extract to `jits/clips/`
3. **Process** → transcribe + generate markdown → `jits/Techniques/`
