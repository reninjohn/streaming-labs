# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Renin John

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "hls_probe.py"


def test_media_playlist_summary(tmp_path):
    media = tmp_path / "media.m3u8"
    media.write_text(
        "#EXTM3U\n#EXT-X-TARGETDURATION:4\n#EXTINF:4.0,\na.ts\n#EXTINF:4.0,\nb.ts\n#EXTINF:4.0,\nc.ts\n#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    res = subprocess.run([sys.executable, str(PROBE), str(media)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    out = res.stdout
    assert "Playlist type: MEDIA" in out
    assert "Segments: 3" in out
    assert "Target duration: 4.0" in out
    assert "Total duration (s): 12.000" in out
    assert "Average segment duration (s): 4.000" in out
