# streaming-labs

Lightweight utilities for inspecting HLS playlists, plus concise FFmpeg recipes.

**Purpose:** Provide a tiny, dependency-free reference you can run locally to explore HLS fundamentals (media vs master playlists, segment timing) and a few practical FFmpeg commands.

---

## Contents

- `tools/hls_probe.py` — zero-dependency **HLS media-playlist probe** that prints segment stats
- `ffmpeg.md` — short, production-minded FFmpeg/ffprobe commands for HLS work
- `examples/` — tiny example playlists you can use offline:
  - `demo_media.m3u8` (media playlist)
  - `demo_master.m3u8` (master playlist)

---

## Requirements

- Python **3.10+** (tested on 3.13)
- No additional Python packages are required to run the probe

---

## Quick start

```bash
# 1) Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .\.venv\Scripts\Activate.ps1

# 2) (Optional) Developer tools for formatting/linting/tests
python -m pip install --upgrade pip
python -m pip install black ruff pytest
```

> The probe itself has **no external dependencies** — the dev tools are only for formatting/linting/tests.

---

## HLS probe

Probe a **media** playlist (`.m3u8`) and print a summary of segment timing:

```bash
python tools/hls_probe.py /path/to/media.m3u8
# or a URL:
python tools/hls_probe.py https://example.com/path/to/media.m3u8
```

**Example output**
```
Playlist type: MEDIA
Segments: 3
Target duration: 4.0
Total duration (s): 12.000
Average segment duration (s): 4.000
```

If you pass a **master** playlist, the tool detects it and exits non-zero:

```
Playlist type: MASTER (variants present).
Tip: run this tool on a **media** playlist (the one with #EXTINF segments).
```

> **Why the distinction?** Master playlists describe variants (bitrate/resolution/codecs).
> Media playlists contain segments with `#EXTINF:<seconds>`, which is what this probe analyzes.

**Try with the included examples**
```bash
python tools/hls_probe.py examples/demo_media.m3u8    # prints stats, exit 0
python tools/hls_probe.py examples/demo_master.m3u8   # reports MASTER, exit 1
```

---

## FFmpeg recipes

See [`ffmpeg.md`](./ffmpeg.md) for:
- Inspecting inputs with `ffprobe`
- Transmux MP4 → HLS without re-encoding
- Transcoding to HLS with aligned keyframes (2s segments)

---

## Installing FFmpeg / ffprobe (optional)

The HLS probe does **not** require FFmpeg. These tools are only needed if you want to generate or inspect media locally for the recipes in `ffmpeg.md`.

- **macOS (Homebrew)**
  ```bash
  brew install ffmpeg
  ```

- **Ubuntu / Debian**
  ```bash
  sudo apt-get update && sudo apt-get install -y ffmpeg
  ```

- **Windows (winget or Chocolatey)**
  ```powershell
  winget install --id Gyan.FFmpeg
  # or
  choco install ffmpeg
  ```

**Verify:**
```bash
ffmpeg -version
ffprobe -version
```

---

## Development

This repo keeps **policy** in `pyproject.toml` so editor, CLI, and CI agree.

Common commands:

```bash
# Lint (Ruff) and apply safe fixes
ruff check . --fix

# Format (Black)
black .

# Run tests (pytest)
pytest -q
```

If you use VS Code, `.vscode/settings.json` enables:
- format on save (Black)
- Ruff code actions on save (fixes + import sorting)
- pytest discovery (`tests/`)

---

## Notes & future ideas

- **Current scope:** media playlist stats — count, target duration, total/average segment length; warn if the longest segment is > 2x the average (simple QoE sanity check).
- **Possible next steps:**
  - Master playlist summary (bandwidth/resolution/codecs)
  - Spec check: assert that each `#EXTINF` ≤ `#EXT-X-TARGETDURATION`
  - LL-HLS awareness (`#EXT-X-PART`, `#EXT-X-PRELOAD-HINT`)

---

## License

MIT — see [LICENSE](./LICENSE).
