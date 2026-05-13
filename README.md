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

## 🎮 Usage

1. **Paste URL** - YouTube video or playlist link
2. **Choose Format** - Audio (MP3) or Video (MP4)
3. **Select Quality** - Bitrate for audio, resolution for video
4. **Set Fragments** - Higher = faster downloads (default 10)
5. **Pick Folder** - Where to save downloaded files
6. **Click START** - Watch the progress!

### Playlist Range Examples
- `1-10` - First 10 videos
- `5,10,15` - Specific tracks
- `1-5,10,15-20` - Mixed range

### Getting 18+ Content
Click **"Login to YouTube"** button, enter your browser name (chrome, firefox, edge), and make sure you're logged into YouTube in that browser.

## 📦 Dependencies

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading backend
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI widgets
- [requests](https://docs.python-requests.org/) - HTTP requests for updates
- [packaging](https://packaging.pypa.io/) - Version comparison

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The core downloading engine
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Beautiful UI components
