# 🎬 Piotr's Stream Dumper

A clean, modern desktop tool for capturing live streams directly to MKV files using **ffmpeg** — built with Python and CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![ffmpeg](https://img.shields.io/badge/Requires-ffmpeg-orange?style=flat-square)

---

## Screenshot

> _Dark theme UI with status indicator, stream URL input, and one-click dump controls._
> https://github.com/Piotrwie85/Piotrs-Stream-Dumper/blob/main/Screen.jpg?raw=true

---

## Features

- Paste or type any stream URL (RTMP, HLS, HTTP, etc.)
- Output saved directly as `.mkv` with stream copy — no re-encoding
- Live status indicator (green / orange / red)
- Right-click context menu on all input fields (Cut, Copy, Paste, Select All)
- Start button disables while a dump is running to prevent double-starts
- Windows-safe stop — uses `process.terminate()` for clean shutdown
- Dark title bar on Windows 10/11 via DWM API
- Saves path shown in the UI so you always know where your file is going

---

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.10+ | [python.org](https://www.python.org/downloads/) |
| ffmpeg | Must be on your system PATH — see below |
| customtkinter | Installed via pip |

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/Piotrwie85/piotrs-stream-dumper.git
cd piotrs-stream-dumper
```

### 2. Install Python dependencies

```bash
pip install customtkinter
```

### 3. Install ffmpeg

**Windows (recommended via winget):**
```bash
winget install ffmpeg
```

**Or download manually** from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add the `bin/` folder to your system `PATH`.

**Verify ffmpeg is working:**
```bash
ffmpeg -version
```

---

## Usage

```bash
python dump.py
```

1. Paste or type your stream URL into the **Stream URL** field
2. Enter a filename (without extension) into the **Output Filename** field
3. Click **▶ Start Dump**
4. Click **■ Stop** when done — the `.mkv` file will be in the same folder as `dump.py`

### Supported URL formats

| Format | Example |
|---|---|
| RTMP | `rtmp://live.example.com/stream/key` |
| HLS | `https://example.com/stream/index.m3u8` |
| HTTP/S direct | `https://example.com/stream.ts` |
| UDP/RTP | `udp://239.0.0.1:5000` |

> Any URL that ffmpeg can read will work.

---

## How it works

The app calls ffmpeg with the `-c copy` flag, meaning the audio and video streams are **copied as-is** into an MKV container — no transcoding, no quality loss, minimal CPU usage.

```
ffmpeg -y -i <URL> -c copy -f matroska <output.mkv>
```

ffmpeg runs in a background thread so the UI stays responsive. Output is monitored line-by-line for errors, which are surfaced in the status bar.

---

## File structure

```
piotrs-stream-dumper/
├── dump.py        # Main application
└── README.md      # This file
```

---

## Troubleshooting

**"ffmpeg not found" error**
ffmpeg is not installed or not on your PATH. See the [Installation](#installation) section.

**Dump stops immediately / status turns red**
The stream URL may be invalid, expired, or require authentication. Test it directly in ffmpeg from the command line first:
```bash
ffmpeg -i "YOUR_URL_HERE"
```

**Right-click paste not working**
Make sure you are right-clicking directly inside one of the input fields. The context menu (Cut / Copy / Paste / Select All) is bound to those fields only.

**Output file is empty or corrupt**
This usually means ffmpeg couldn't read the stream format. Try a different container or check if the stream requires special flags (e.g., `-user_agent`, `-headers`).

---

## Building a standalone .exe (optional)

If you want to distribute the app without requiring Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "PiotrsStreamDumper" dump.py
```

The `.exe` will appear in the `dist/` folder. Note: ffmpeg still needs to be installed separately on the target machine.

---

## License

MIT — do whatever you want with it.

---

## Acknowledgements

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky — modern UI widgets for tkinter
- [ffmpeg](https://ffmpeg.org/) — the backbone of the actual stream capture
