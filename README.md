# ClipJits

A two-step command-line tool for creating Brazilian Jiu Jitsu technique cards from instructional videos. ClipJits enables efficient video clipping during study sessions, followed by batch AI-powered processing to generate technique summaries in Obsidian-compatible markdown format.

## Features

- Download videos from YouTube, Instagram, Reddit, and X
- Mark and extract video clips using MPV media player with simple keyboard shortcuts
- Batch process clips with automatic transcription (OpenAI Whisper)
- Generate technique summaries using LLM (OpenAI, Anthropic)
- Create Obsidian-compatible markdown files with embedded video references
- Group related clips by label into single technique cards

## Requirements

### System Dependencies

- **Python 3.10+**
- **FFmpeg** - Video processing
- **MPV** - Media player with scripting support

#### Installing System Dependencies

**Windows:**
```bash
# Install FFmpeg
winget install ffmpeg

# Install MPV
winget install mpv
```

**macOS:**
```bash
brew install ffmpeg mpv
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg mpv python3-pip
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ClipJits
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate -- On Windows Bash: source venv/Scripts/activate
```

3. Install ClipJits:
```bash
pip install -e .
```

4. Create configuration file:
```bash
cp .env.example .env
```

5. Edit `.env` file with your settings:
```bash
# Required: Set your API keys
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here

# Optional: Customize paths
OBSIDIAN_VAULT_PATH=~/Documents/ObsidianVault/BJJ/techniques
SOURCE_VIDEOS_DIR=./source-videos
CLIPS_OUTPUT_DIR=./clips
```

## Usage

### Step 1: Download and Clip Videos

#### Download a video
```bash
clipjits download <url>
clipjits download <url> --quality 720p
```

#### Watch and mark clips
```bash
clipjits watch path/to/video.mp4
```

**MPV Keybindings:**
- `s` - Mark clip start timestamp
- `e` - Mark clip end timestamp
- `c` - Commit clip to queue (prompts for label)
- `q` - Quit MPV

**Label naming convention:** Use numbered labels for related clips (e.g., `armbar1`, `armbar2`, `armbar3`) to group them into a single technique card.

#### Manage clip queue
```bash
# View queued clips
clipjits queue list

# Edit queue (remove clips or update labels)
clipjits queue edit

# Clear entire queue
clipjits queue clear
```

#### Extract clips
```bash
clipjits extract
clipjits extract --output-dir ./my-clips
```

### Step 2: Process Clips

Process extracted clips to generate technique cards:

```bash
clipjits process ./clips
```

**Advanced options:**
```bash
# Specify output directory
clipjits process ./clips --output-dir ~/obsidian-vault/BJJ

# Use different Whisper model
clipjits process ./clips --model medium

# Use Anthropic instead of OpenAI
clipjits process ./clips --llm-provider anthropic

# Skip transcription (use existing .txt files)
clipjits process ./clips --skip-transcription

# Resume processing (skip already processed clips)
clipjits process ./clips --resume
```

## Workflow Example

Complete workflow from video to technique card:

```bash
# 1. Download instructional video
clipjits download "https://youtube.com/watch?v=..."

# 2. Watch and mark techniques
clipjits watch source-videos/bjj-armbar-tutorial.mp4
# In MPV: press 's' at start, 'e' at end, 'c' to commit (label: armbar1)
# Repeat for multiple techniques or multiple clips of same technique

# 3. Review queue
clipjits queue list

# 4. Extract clips
clipjits extract

# 5. Process clips into technique cards
clipjits process ./clips

# Done! Markdown files are in your Obsidian vault
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

## Output Format

Generated markdown files follow this structure:

```markdown
# Armbar from Guard

**Category**: Submission
**Source**: bjj-tutorial_armbar1.mp4

## Steps
1. Control opponent's posture by grabbing behind the head
2. Place foot on opponent's hip
3. Swing leg over opponent's shoulder
4. Fall back while securing the arm
5. Bridge hips and apply pressure to elbow

## Concepts & Details
- Keep knees tight together
- Control the wrist with both hands
- Thumb points up to prevent escape
- Common mistake: Not controlling posture first

## Video
![[bjj-tutorial_armbar1.mp4]]
![[bjj-tutorial_armbar2.mp4]]
```

## Troubleshooting

### Cannot run `clipjits` command

**Error**: `'clipjits' is not recognized` or `command not found`

**Solution**: Use `python -m clipjits` instead:
```bash
python -m clipjits --help
python -m clipjits download <url>
python -m clipjits watch video.mp4
```

If you prefer using just `clipjits`, either:
- **Use a virtual environment** (recommended):
  ```bash
  source venv/Scripts/activate  # Windows Bash
  clipjits --help
  ```
- **Add to PATH**: Add Python Scripts directory to your system PATH
  - Windows: `C:\Users\<username>\AppData\Roaming\Python\Python3XX\Scripts`
  - macOS/Linux: Usually already in PATH

### MPV doesn't launch
- Verify MPV is installed: `mpv --version`
- Check that video file exists and is readable

### Clip extraction fails
- Verify FFmpeg is installed: `ffmpeg -version`
- Check that source video path in queue is correct

### Download fails with HTTP 403 error

**Error**: `HTTP Error 403: Forbidden` when downloading from YouTube

**Solutions**:
1. **Update yt-dlp** (most common fix):
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Use cookies** (if updating doesn't work):
   - Install browser extension: "Get cookies.txt LOCALLY"
   - Export cookies from YouTube while logged in
   - Use: `clipjits download <url> --cookies cookies.txt`

### Transcription is slow
- Use smaller Whisper model (set `WHISPER_MODEL_SIZE=tiny` in `.env`)
- Consider GPU acceleration (requires CUDA/ROCm setup)

### LLM generation fails
- Verify API key is set correctly in `.env`
- Check API key has sufficient credits
- Verify internet connection

### MPV label input issues

When you press `c` to commit a clip:
- The video will pause
- Look at your **terminal window** (not MPV window)
- You'll see a prompt: `Enter clip label (or press Enter to skip):`
- Type your label and press Enter
- Video will resume after saving

**Note**: You may see "No key binding found" messages while typing - these are harmless and expected.

### Queue file location
- Default: `~/.clipjits/clip_queue.json`
- Can be customized via `MPV_IPC_SOCKET` in `.env`

## Advanced Usage

### Using Local Videos

You can work with existing `.mp4` files without downloading:

```bash
clipjits watch /path/to/your/video.mp4
```

### Batch Downloading

Create a text file with URLs (one per line) and download them:

```bash
while read url; do clipjits download "$url"; done < urls.txt
```

### Custom Clip Naming

Clips are automatically named as: `{source-video-name}_{label}.mp4`

Use descriptive labels during clipping for better organization.

## Project Structure

```
ClipJits/
├── clipjits/           # Main package
│   ├── __init__.py
│   ├── __main__.py     # Module entry point
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   ├── download.py     # Video downloader
│   ├── clip.py         # Clip manager and MPV integration
│   ├── process.py      # Batch processor
│   └── utils.py        # Utility functions
├── mpv-scripts/        # MPV Lua scripts
│   └── clip-marker.lua # Clip marking script
├── .env.example        # Example configuration
├── pyproject.toml      # Package configuration
└── README.md           # This file
```

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
