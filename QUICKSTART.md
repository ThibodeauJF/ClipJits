# Quick Start Guide

## Installation Complete!

ClipJits has been successfully installed. Since you're on Windows, the CLI command may not be directly on your PATH. Here are the ways to use ClipJits:

### Option 1: Use Python Module (Recommended)

Run commands using Python's module syntax:

```bash
python -m clipjits.cli --help
python -m clipjits.cli download <url>
python -m clipjits.cli watch video.mp4
python -m clipjits.cli queue list
python -m clipjits.cli extract
python -m clipjits.cli process ./clips
```

### Option 2: Add Scripts to PATH

The clipjits.exe file was installed to:
```
C:\Users\jf\AppData\Roaming\Python\Python313\Scripts
```

You can add this directory to your system PATH to use `clipjits` directly.

**To add to PATH:**
1. Press Windows + X and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", find and edit "Path"
5. Add: `C:\Users\jf\AppData\Roaming\Python\Python313\Scripts`
6. Restart your terminal

After adding to PATH, you can use:
```bash
clipjits --help
clipjits download <url>
```

### Option 3: Create a Batch File Alias

Create a file called `cj.bat` in your project directory:

```batch
@echo off
python -m clipjits.cli %*
```

Then use:
```bash
cj --help
cj download <url>
cj watch video.mp4
```

## Configuration

Before using ClipJits, edit your `.env` file and add your API keys:

```bash
# For OpenAI
OPENAI_API_KEY=sk-your-key-here

# OR for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Example Workflow

```bash
# 1. Download a video
python -m clipjits.cli download "https://youtube.com/watch?v=example"

# 2. Watch and mark clips (MPV will open)
python -m clipjits.cli watch source-videos/your-video.mp4
# In MPV: press 's' for start, 'e' for end, 'c' to commit (enter label: armbar1)

# 3. View queue
python -m clipjits.cli queue list

# 4. Extract clips
python -m clipjits.cli extract

# 5. Process into technique cards
python -m clipjits.cli process ./clips
```

## System Requirements

Make sure you have installed:
- **FFmpeg**: `winget install ffmpeg`
- **MPV**: `winget install mpv`

Test they're installed:
```bash
ffmpeg -version
mpv --version
```

## Next Steps

1. Edit `.env` with your API keys and preferences
2. Try downloading a test video
3. Practice marking clips in MPV
4. Process your first technique card

See README.md for complete documentation.
