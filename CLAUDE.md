# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Overview

This is a Python virtual environment for OpenAI Whisper, an automatic speech recognition (ASR) system. The environment is located at `/Users/greg/Documents/whisper_env` and uses Python 3.13.5.

## Project Structure and Architecture

### Main Application
- **`audio_transcriber.py`** - Main audio transcription script with dual output modes
- **`audio_transcriber_old.py`** - Legacy version (backup)
- **`audio_folder_action.applescript`** - Apple Script for automated folder monitoring
- **`README.md`** - User documentation in Russian with usage instructions

### Whisper Installation
The Whisper library is installed via pip in the virtual environment at:
- **Location**: `/Users/greg/Documents/whisper_env/lib/python3.13/site-packages/whisper/`
- **Core modules**: `audio.py`, `transcribe.py`, `decoding.py`, `model.py`, `tokenizer.py`
- **Assets**: Pre-trained tokenizers and mel filters in `assets/` directory

### Key Dependencies
- **openai-whisper 20250625** - Main ASR system
- **PyTorch 2.8.0** - Deep learning framework
- **NumPy 2.2.6** - Numerical computing
- **Standard library**: `os`, `glob`, `pathlib`, `json`, `datetime`, `argparse`

## Audio Transcriber Usage

### Basic Commands

**Activate Environment**:
```bash
source /Users/greg/Documents/whisper_env/bin/activate
```

**Run Transcriber** (from any directory with audio files):
```bash
python /Users/greg/Documents/whisper_env/audio_transcriber.py
```

**With Custom Model**:
```bash
python /Users/greg/Documents/whisper_env/audio_transcriber.py --model large-v3-turbo
```

**List Available Models**:
```bash
python /Users/greg/Documents/whisper_env/audio_transcriber.py --list-models
```

### Supported Audio Formats
- MP3, WAV, M4A, FLAC, OGG, WMA, AAC

### Output Files
The script creates two markdown files per audio file:
1. **`filename.md`** - Simple transcription text only
2. **`filename_accurate.md`** - Detailed technical report with timestamps, segments, and metadata

## Application Architecture

### Core Functions (`audio_transcriber.py`)
- **`get_audio_files()`** (line 23) - Scans current directory for supported audio formats
- **`transcribe_audio_file()`** (line 138) - Main transcription logic with error handling
- **`create_simple_markdown()`** (line 48) - Generates basic transcription output
- **`create_detailed_markdown()`** (line 66) - Creates comprehensive technical report
- **`format_duration()`** (line 34) - Converts seconds to human-readable time format

### Key Features
- **Model Selection**: Defaults to `medium`, configurable via `--model` argument
- **File Skipping**: Automatically skips already processed files
- **Error Handling**: Continues processing other files if one fails
- **Batch Processing**: Processes all audio files in current directory
- **Detailed Logging**: Progress indicators with emoji feedback

## Available Whisper Models
- `tiny`, `tiny.en` - Fastest, least accurate
- `base`, `base.en` - Balanced speed/accuracy  
- `small`, `small.en` - Good accuracy
- `medium`, `medium.en` - High accuracy (default)
- `large-v1`, `large-v2`, `large-v3`, `large` - Highest accuracy
- `turbo`, `large-v3-turbo` - Latest optimized models

Models ending in `.en` are English-only; others support multilingual transcription.

## Development Commands

**Check Installed Packages**:
```bash
source /Users/greg/Documents/whisper_env/bin/activate && pip list
```

**Install Additional Dependencies**:
```bash
source /Users/greg/Documents/whisper_env/bin/activate && pip install [package-name]
```

**Run with Debugging** (modify script line 194 for different default model):
```python
# In audio_transcriber.py, line 194
default='large-v3-turbo'  # Change from 'medium' for better accuracy
```

## Automated Folder Monitoring (Apple Script)

### Apple Script Integration
The project includes `audio_folder_action.applescript` for automated processing of audio files dropped into a specific folder.

### Folder Action Setup
**Target Folder**: `~/Desktop/Recognize`

**Installation Steps**:
1. Open **Script Editor** (Applications → Utilities)
2. Copy contents from `audio_folder_action.applescript`
3. Save as **Folder Action** for the Recognize folder

### Automation Features
- **Automatic Detection**: Monitors for audio files with extensions: .mp3, .wav, .m4a, .flac, .ogg, .wma, .aac
- **Visual Feedback**: Shows macOS notification when processing starts
- **Terminal Integration**: Opens Terminal window showing the transcription process
- **Same-Folder Output**: Creates markdown files in the Recognize folder alongside audio files

### Apple Script Architecture (`audio_folder_action.applescript`)
- **`adding folder items to`** (line 1) - Main folder action handler
- **`isAudioFile()`** (line 35) - File extension validation function
- **Terminal Integration** (lines 23-26) - Launches Terminal with Python environment
- **Notification System** (line 13) - macOS notification display