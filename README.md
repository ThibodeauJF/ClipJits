# ClipJits
<img width="2391" height="1174" alt="flow" src="https://github.com/user-attachments/assets/98bdc68d-b92b-4bf7-90ea-7f8652229426" />
Easily BJJ technique cards from instructional videos with AI-powered summaries. Used to do this manually but it happened to take a shit ton of time!

## Requirements

- Python 3.10+
- FFmpeg: `winget install ffmpeg` (Windows) or `brew install ffmpeg` (macOS)
- MPV: `winget install mpv` (Windows) or `brew install mpv` (macOS)

## Installation

```bash
git clone <repository-url>
cd ClipJits
pip install -e .
cp .env.example .env
```

Edit `.env` with your API key:
```bash
OPENAI_API_KEY=your-key-here
VAULT_PATH=./jits
```

## Usage

![meirl](https://github.com/user-attachments/assets/3d8b4413-944a-4752-aa3e-14c0d4893220)
_(no one named "Claude" was injured during the making of this, I swear...)_

**Note:** If `clipjits` command not found, use `python -m clipjits` instead.

```bash
# 1. Download video
clipjits download "https://youtube.com/watch?v=..."

# 2. Watch & mark clips (s=start, e=end, c=commit)
clipjits watch jits/downloads/video.mp4

# 3. Process clips (transcribe + generate technique cards)
clipjits process
```

**Processing options:**
```bash
clipjits process --model medium              # Better transcription
clipjits process --llm-provider anthropic    # Use Claude
clipjits process --resume                    # Skip already processed
```

## Vault Structure

All data organized under `VAULT_PATH`:

```
jits/
  clips/              # Active clips ready to process
  clips/processed/    # Processed clips (archived)
  downloads/          # Downloaded videos
  Techniques/         # Generated markdown files
  Media/              # Media files referenced in markdown
```

## Configuration

Key settings in `.env`:

| Setting | Description | Default |
|---------|-------------|---------|
| `VAULT_PATH` | Main vault directory | `./jits` |
| `DEFAULT_VIDEO_QUALITY` | Video download quality | `1080p` |
| `WHISPER_MODEL_SIZE` | Whisper model (tiny/base/small/medium/large) | `base` |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | `openai` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |

## Troubleshooting

**Command not found:** Use `python -m clipjits` instead

**YouTube 403 error:** Run `pip install --upgrade yt-dlp`

**MPV label input:** After pressing `c`, enter label in terminal (required)

**Slow transcription:** Set `WHISPER_MODEL_SIZE=tiny` in `.env`
