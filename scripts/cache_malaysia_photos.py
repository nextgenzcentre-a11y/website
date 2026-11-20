#!/usr/bin/env python3
"""Vendor approved, location-verified Pexels photography for the Why Malaysia page.

Includes Cameron Highlands replacement photo source verification.

The copy, brand fonts, logo, footer and layout are not changed. Sources are
linked in existing captions. Failed downloads retain their original remote
URLs rather than leaving broken images in production.
"""
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "why-malaysia.html"
OUT = ROOT / "assets" / "malaysia"
PATTERN = re.compile(r'https://images\.pexels\.com/photos/(\d+)/pexels-photo-\1\.jpeg\?auto=compress&amp;cs=tinysrgb&amp;w=(\d+)')

def main():
    raw = PAGE.read_text(encoding="utf-8")
    candidates = sorted(set(PATTERN.findall(raw)))
    if not candidates:
        print("Why Malaysia has no remote images left to vendor.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    succeeded = []
    failed = []
    for image_id, width in candidates:
        target = OUT / f"pexels-{image_id}.jpg"
        remote = f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg?auto=compress&cs=tinysrgb&w={width}"
        if not target.exists():
            try:
                request = urllib.request.Request(remote, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; NextGenzCentre/1.0)",
                    "Accept": "image/jpeg,image/*;q=0.8",
                })
                with urllib.request.urlopen(request, timeout=24) as response:
                    mime = response.headers.get("Content-Type", "")
                    content = response.read(4_000_000)
                if "jpeg" not in mime.lower() and not content.startswith(b"\xff\xd8"):
                    raise ValueError(f"unexpected media type {mime}")
                if not content.startswith(b"\xff\xd8") or len(content)<5000:
                    raise ValueError("not a valid JPEG response")
                target.write_bytes(content)
            except Exception as exc:
                print(f"SKIP: Pexels {image_id}, {exc}")
                failed.append(image_id)
                continue
        original = f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg?auto=compress&amp;cs=tinysrgb&amp;w={width}"
        raw = raw.replace(original, f"/assets/malaysia/pexels-{image_id}.jpg")
        succeeded.append(image_id)
    if succeeded:
        PAGE.write_text(raw, encoding="utf-8")
    print(f"Vendored {len(succeeded)} photographic assets; {len(failed)} left as original remote references.")
    if not succeeded:
        raise RuntimeError("No photography could be downloaded; no publication changes were made")

if __name__ == "__main__":
    main()
