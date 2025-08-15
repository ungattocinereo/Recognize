# 🎵 Recognize - AI Audio Transcription System

Advanced automatic speech recognition system using OpenAI Whisper with automated macOS integration.

## 🌟 Features

- **Dual Output Modes**: Simple text and detailed technical transcriptions
- **Automated Processing**: Drop-and-go functionality with macOS Folder Actions
- **Multi-format Support**: MP3, WAV, M4A, FLAC, OGG, WMA, AAC
- **Intelligent Model Selection**: Configurable Whisper models from tiny to large-v3-turbo
- **Enhanced Progress Tracking**: Real-time progress bars with time estimates
- **Smart Notifications**: macOS alerts for start, completion, and errors
- **Queue Management**: Single Terminal processes all files sequentially
- **Intelligent File Management**: Smart filename conflict resolution

## 🏗️ Project Architecture

### Core Components

- **`audio_transcriber.py`** - Main Python transcription engine
- **`audio_folder_action.applescript`** - macOS automation script
- **`CLAUDE.md`** - Development documentation for AI assistants

### Two Usage Modes

1. **Manual Mode**: Command-line execution for any directory
2. **Automated Mode**: Drop files into `~/Desktop/Recognize` for automatic processing

## 🚀 Quick Start

### Prerequisites

- Python 3.13.5
- macOS (for automation features)
- 4-6 GB RAM (for large models)

### Installation

1. **Clone the repository**:
```bash
git clone git@github.com:ungattocinereo/Recognize.git
cd Recognize
```

2. **Set up Python virtual environment**:
```bash
python3 -m venv whisper_env
source whisper_env/bin/activate
pip install openai-whisper torch numpy
```

3. **Set up macOS automation** (optional):
   - Open Script Editor
   - Copy contents from `audio_folder_action.applescript`
   - Save as Folder Action for `~/Desktop/Recognize` folder

## 💻 Usage

### Manual Mode

```bash
# Activate environment
source whisper_env/bin/activate

# Navigate to folder with audio files
cd /path/to/your/audio/files

# Run transcription
python /path/to/Recognize/audio_transcriber.py
```

### With Custom Model

```bash
python audio_transcriber.py --model large-v3-turbo
```

### List Available Models

```bash
python audio_transcriber.py --list-models
```

### Automated Mode

1. Ensure Folder Action is set up for `~/Desktop/Recognize`
2. Drop audio files into the Recognize folder
3. Receive notification about queue status and time estimates
4. Watch single Terminal window process files sequentially with progress bars
5. Get completion notifications with text previews
6. Find transcription files in the same folder

## 📄 Output Files

Each audio file generates two markdown files:

### Simple Transcription (`filename.md`)
```markdown
# Транскрипция: audio.mp3

Clean transcribed text without technical details...
```

### Detailed Report (`filename_accurate.md`)
Includes:
- File metadata (size, processing date)
- Detected language
- Timestamped segments
- Technical metrics (confidence scores, duration)
- Complete JSON data for advanced analysis

## 🔧 Configuration

### Model Selection
Available models (in order of accuracy vs speed):
- `tiny`, `tiny.en` - Fastest, basic accuracy
- `base`, `base.en` - Balanced performance
- `small`, `small.en` - Good accuracy
- `medium`, `medium.en` - High accuracy (default)
- `large-v1`, `large-v2`, `large-v3` - Highest accuracy
- `turbo`, `large-v3-turbo` - Latest optimized models

### Supported Audio Formats
MP3, WAV, M4A, FLAC, OGG, WMA, AAC

### Performance Optimization
- Models ending in `.en` are English-only and faster
- Smaller models use less memory and process faster
- First run downloads model to `~/.cache/whisper/`

## 🛠️ Development

### Key Functions (`audio_transcriber.py`)
- `get_audio_files()` - Scans for supported audio formats
- `transcribe_audio_file()` - Core transcription logic
- `create_simple_markdown()` - Generates basic output
- `create_detailed_markdown()` - Creates comprehensive report

### Apple Script Functions (`audio_folder_action.applescript`)
- `adding folder items to` - Main automation handler
- `isAudioFile()` - File type validation
- Terminal integration for visible processing

## 🚨 Troubleshooting

### Common Issues

**"No module named 'whisper'"**
```bash
source whisper_env/bin/activate
pip show openai-whisper
```

**Memory errors with large models**
- Use smaller models (`base`, `small`)
- Close other applications
- Ensure 4+ GB available RAM

**Folder Action not working**
- Check Script Editor for proper Folder Action setup
- Verify folder path: `~/Desktop/Recognize`
- Enable notifications in System Preferences

## 🔋 Performance

- **Processing Speed**: Varies by model size and audio length
- **Memory Usage**: 1-6 GB depending on model
- **Accuracy**: Near-human level with large models
- **Languages**: 99+ languages supported
- **Real-time Factor**: 0.1-0.5x (faster than real-time)

## 📊 System Requirements

- **Minimum**: Python 3.8+, 2 GB RAM, 1 GB storage
- **Recommended**: Python 3.13+, 8 GB RAM, 5 GB storage
- **Optimal**: Apple Silicon Mac, 16 GB RAM, SSD storage

## 🤝 Contributing

This project uses AI-assisted development with Claude Code. See `CLAUDE.md` for development guidelines and architecture details.

## 📜 License

Open source project for educational and personal use.

## 🙏 Acknowledgments

- OpenAI Whisper team for the exceptional ASR model
- Python community for excellent tooling
- macOS Folder Actions for seamless automation