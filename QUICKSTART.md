# Quick Start

## Setup

```bash
pip install -e .
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

Install dependencies:
```bash
winget install ffmpeg mpv  # Windows
# or
brew install ffmpeg mpv    # macOS
```

## Running Commands

If `clipjits` command not found, use `python -m clipjits`:

```bash
clipjits download "https://youtube.com/watch?v=..."
clipjits watch jits/downloads/video.mp4
clipjits process
```

## MPV Controls

- `s` - Mark start
- `e` - Mark end  
- `c` - Commit (enter label in terminal - **required**, extracts immediately)
- `q` - Quit

## Workflow

1. **Download** → saves to `jits/downloads/`
2. **Watch** → mark clips, they extract immediately to `jits/clips/`
3. **Process** → clips move to `jits/clips/processed/`, media to `jits/Media/`, markdown to `jits/Techniques/`

## Tips

- Label is **required** when committing clips
- All filenames use snake_case with 50 character limit
- Clips from same source video are processed together
- Label prompt appears in **terminal**, not MPV window
- Update yt-dlp if downloads fail: `pip install --upgrade yt-dlp`
