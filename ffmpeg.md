# ffmpeg recipes (HLS)

> Core flow: inspect → transmux if possible → transcode with aligned GOPs when needed.

---

## 1) Inspect the input (decide transmux vs transcode)
```bash
ffprobe -hide_banner -i input.mp4
```
**Why:** see container/codec/resolution/duration to choose the right path.

---

## 2) Transmux MP4 → HLS (fastest, no quality loss)
```bash
ffmpeg -i input.mp4 -c copy   -hls_time 4 -hls_playlist_type vod -hls_flags independent_segments   -f hls stream.m3u8
```
**When:** input is already HLS-friendly (e.g., H.264 video + AAC audio).

---

## 3) Transcode to HLS (2s segments, aligned keyframes)
```bash
ffmpeg -i input.mp4   -c:v libx264 -profile:v main -level 4.0   -x264-params keyint=60:min-keyint=60:scenecut=0   -c:a aac -b:a 128k -ar 48000   -hls_time 2 -hls_flags independent_segments -hls_playlist_type vod   -f hls stream.m3u8
```
**When:** codecs aren’t compatible or you need stable segment timing; 2s GOP at ~30fps → `keyint=60`.
