#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Renin John

"""
hls_probe.py — minimal HLS playlist probe (no external deps)

Usage:
  python tools/hls_probe.py <path-or-url-to-m3u8>

Prints: playlist type, segment count, target duration, total/avg segment duration.
Exit code 0 on success; 1 on invalid/unsupported playlists.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from collections.abc import Iterable
from pathlib import Path

EXTM3U = "#EXTM3U"
RE_TARGET = re.compile(r"^#EXT-X-TARGETDURATION:(\d+)", re.MULTILINE)
RE_EXTINF = re.compile(r"^#EXTINF:([0-9]*\.?[0-9]+)", re.MULTILINE)

RE_STREAM_INF = re.compile(r"^#EXT-X-STREAM-INF(?::|,|\s|$)")
RE_MEDIA_ALT = re.compile(r"^#EXT-X-MEDIA(?::|,|\s|$)")  # alt renditions tag (master only)


def _read_text(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://")):
        req = urllib.request.Request(path_or_url, headers={"User-Agent": "hls-probe/0.1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    return Path(path_or_url).read_text(encoding="utf-8", errors="replace")


def _is_master(lines: Iterable[str]) -> bool:
    # MASTER: has #EXT-X-STREAM-INF (variants) or #EXT-X-MEDIA (alt renditions)
    for ln in lines:
        if RE_STREAM_INF.match(ln) or RE_MEDIA_ALT.match(ln):
            return True
    return False


def _probe(lines: Iterable[str]) -> tuple[int, int | None, float, float]:
    """
    Returns:
        (segment_count, target_dur, total_dur, avg_dur)
    """
    text = "\n".join(lines)
    m_target = RE_TARGET.search(text)
    target = float(m_target.group(1)) if m_target else None

    seg_durs = [float(m.group(1)) for m in RE_EXTINF.finditer(text)]
    count = len(seg_durs)
    total = sum(seg_durs)
    avg = (total / count) if count else 0.0
    return count, target, total, avg


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/hls_probe.py <path-or-url-to-m3u8>", file=sys.stderr)
        return 1

    src = argv[1]
    try:
        raw = _read_text(src)
    except Exception as e:
        print(f"Error: failed to read playlist: {e}", file=sys.stderr)
        return 1

    lines = [s for ln in raw.splitlines() if (s := ln.strip())]
    if not lines or lines[0] != EXTM3U:
        print("Error: not an M3U8 playlist (missing #EXTM3U).", file=sys.stderr)
        return 1

    if _is_master(lines):
        print(
            "Playlist type: MASTER (master-only tag present).\n"
            "Tip: run this tool on a media playlist (with #EXTINF segments).",
            file=sys.stderr,
        )
        return 1

    count, target, total, avg = _probe(lines)
    print(
        "Playlist type: MEDIA\n"
        f"Segments: {count}\n"
        f"Target duration: {target if target is not None else 'N/A'}\n"
        f"Total duration (s): {total:.3f}\n"
        f"Average segment duration (s): {avg:.3f}"
    )

    if count:
        max_seg = max((float(m.group(1)) for ln in lines if (m := RE_EXTINF.match(ln))))
        if max_seg > 2 * avg:
            print(f"Note: longest segment {max_seg:.3f}s > 2x avg {avg:.3f}s.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
