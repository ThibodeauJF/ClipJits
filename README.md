# ClipJits

Create BJJ technique cards from instructional videos:
1. Mark clips in MPV with keyboard shortcuts (extracts immediately)
2. Batch process with AI to generate markdown summaries

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

**Note:** If `clipjits` command not found, use `python -m clipjits` instead.

```bash
# 1. Download video (saved to jits/downloads/)
clipjits download "https://youtube.com/watch?v=..."

# 2. Mark and extract clips in MPV
# Press s=start, e=end, c=commit (label required, extracts immediately)
clipjits watch jits/downloads/video.mp4

# 3. Process clips (transcribe + generate technique cards)
clipjits process
```

**Processing options:**
```bash
clipjits process --model medium              # Better transcription
clipjits process --llm-provider anthropic   # Use Claude
clipjits process --resume                   # Skip processed
```



## Configuration

Configuration is managed via `.env` file. See `.env.example` for all available options.

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|------|
| `VAULT_PATH` | Main vault directory (contains all subfolders) | `./jits` |
| `DEFAULT_VIDEO_QUALITY` | Video download quality | `1080p` |
| `WHISPER_MODEL_SIZE` | Whisper model (tiny/base/small/medium/large) | `base` |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | `openai` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |

### Vault Structure

All data is organized under `VAULT_PATH` (default: `./jits/`):

```
jits/
  clips/              # Active clips ready to process
  clips/processed/    # Processed clips (moved here after processing)
  downloads/          # Downloaded videos
  Techniques/         # Generated markdown files
  Media/              # Media files referenced in markdown
```

### Whisper Model Sizes

- `tiny` - Fastest, least accurate (~1GB RAM)
- `base` - Good balance (~1GB RAM) **[Default]**
- `small` - Better accuracy (~2GB RAM)
- `medium` - High accuracy (~5GB RAM)
- `large` - Best accuracy (~10GB RAM)



## Workflow Details

1. **Download**: Videos are saved to `jits/downloads/`
2. **Watch & Clip**: Clips are extracted immediately to `jits/clips/` when you commit (press 'c')
3. **Process**: Clips are transcribed, analyzed, and moved to `jits/clips/processed/`. Media files are copied to `jits/Media/` with proper naming, and markdown files are saved to `jits/Techniques/`

## Troubleshooting

**Command not found:** Use `python -m clipjits` instead of `clipjits`

**YouTube 403 error:** Run `pip install --upgrade yt-dlp`

**MPV label input:** After pressing `c`, look at terminal (not MPV) to enter label (required)

**Slow transcription:** Set `WHISPER_MODEL_SIZE=tiny` in `.env`

**Clips from same video:** Clips from the same source video are processed together into one technique card
