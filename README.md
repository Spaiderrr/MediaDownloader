# Media Downloader Pro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6.svg)](https://www.microsoft.com/windows)

A powerful GUI application for downloading videos and audio from YouTube and other supported sites. Built with Python, yt-dlp, and CustomTkinter.

## ✨ Features

- 🎵 **Audio Download** - MP3, M4A, OGG, OPUS, FLAC formats with quality selection (320/256/128 kbps)
- 🎬 **Video Download** - MP4, WebM, MKV containers with resolution selection (4K, 2K, 1080p, 720p, Best)
- 📁 **Playlist Support** - Download entire playlists or select specific tracks (e.g., 1-5,10,15-20)
- ⚡ **Speed Optimization** - Configurable concurrent fragment downloads (1-20)
- 🌍 **Multi-language** - Russian and English interface with easy switching
- 🔄 **Auto-update Check** - Built-in yt-dlp version checker
- 🔞 **Age-restricted Content** - Cookie import from browsers (Chrome, Firefox, Edge, Opera, Brave)
- 💾 **Settings Persistence** - Remembers your last path, quality, format, and language
- 📊 **Real-time Progress** - Speed, ETA, and file size display
- 🛑 **Cancel Support** - Stop downloads at any time
- 📝 **Detailed Logging** - Everything is logged to a text area

## 📋 Requirements

- Windows 10 / 11 (64-bit)
- [ffmpeg](https://ffmpeg.org/download.html) (for audio conversion and video merging)

## 🚀 Installation

### Option 1: Download Installer (Recommended)
1. Go to the [Releases](https://github.com/YOUR_USERNAME/YTDWLv1/releases) page
2. Download `Media_Downloader-setup.exe`
3. Run the installer and follow the instructions

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YTDWLv1.git
cd YTDWLv1

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download ffmpeg and place it in ffmpeg/bin/
# Download from: https://ffmpeg.org/download.html

# Run the application
python main.py
