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
clipjits watch source-videos/video.mp4
clipjits extract
clipjits process ./clips
```

## MPV Controls

- `s` - Mark start
- `e` - Mark end  
- `c` - Commit (enter label in terminal)
- `q` - Quit

## Tips

- Use numbered labels (`armbar1`, `armbar2`) to group clips into one card
- Label prompt appears in **terminal**, not MPV window
- Update yt-dlp if downloads fail: `pip install --upgrade yt-dlp`
