# ClipJits

Create BJJ technique cards from instructional videos:
1. Mark clips in MPV with keyboard shortcuts
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
OBSIDIAN_VAULT_PATH=~/path/to/vault
```

## Usage

**Note:** If `clipjits` command not found, use `python -m clipjits` instead.

```bash
# 1. Download video
clipjits download "https://youtube.com/watch?v=..."

# 2. Mark clips in MPV (s=start, e=end, c=commit with label)
clipjits watch source-videos/video.mp4

# 3. Extract clips
clipjits extract

# 4. Generate technique cards
clipjits process ./clips
```

**Queue management:**
```bash
clipjits queue list      # View clips
clipjits queue edit      # Edit/remove clips
clipjits queue clear     # Clear all
```

**Options:**
```bash
clipjits process ./clips --model medium              # Better transcription
clipjits process ./clips --llm-provider anthropic   # Use Claude
clipjits process ./clips --resume                   # Skip processed
```



## Configuration

Configuration is managed via `.env` file. See `.env.example` for all available options.

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `SOURCE_VIDEOS_DIR` | Directory for downloaded videos | `./source-videos` |
| `CLIPS_OUTPUT_DIR` | Directory for extracted clips | `./clips` |
| `OBSIDIAN_VAULT_PATH` | Output directory for markdown files | `~/Documents/ObsidianVault/BJJ/techniques` |
| `DEFAULT_VIDEO_QUALITY` | Video download quality | `1080p` |
| `WHISPER_MODEL_SIZE` | Whisper model (tiny/base/small/medium/large) | `base` |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | `openai` |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |

### Whisper Model Sizes

- `tiny` - Fastest, least accurate (~1GB RAM)
- `base` - Good balance (~1GB RAM) **[Default]**
- `small` - Better accuracy (~2GB RAM)
- `medium` - High accuracy (~5GB RAM)
- `large` - Best accuracy (~10GB RAM)



## Troubleshooting

**Command not found:** Use `python -m clipjits` instead of `clipjits`

**YouTube 403 error:** Run `pip install --upgrade yt-dlp`

**MPV label input:** After pressing `c`, look at terminal (not MPV) to enter label

**Slow transcription:** Set `WHISPER_MODEL_SIZE=tiny` in `.env`

**Grouped clips:** Use numbered labels (e.g., `armbar1`, `armbar2`) to combine into one card
