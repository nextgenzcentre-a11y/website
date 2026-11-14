#!/usr/bin/env python3
"""Preserve and enhance the original NextGenz homepage hero without changing its composition.

The original 1832px WebP is kept as hero-original.webp. The 7680px file is a
high-resolution resampling master; interpolation does not create genuinely
photographed detail that was absent from the original.
"""
from pathlib import Path
import shutil

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

base = Path("assets/nextgenz-v7/sections")
live = base / "hero.webp"
source = base / "hero-original.webp"
master = base / "hero-8k.webp"
mobile = base / "hero-mobile.webp"

if not source.exists():
    shutil.copy2(live, source)

with Image.open(source) as loaded:
    image = ImageOps.exif_transpose(loaded).convert("RGB")

image = ImageEnhance.Contrast(image).enhance(1.025)
image = ImageEnhance.Color(image).enhance(1.018)

def enhance(width: int, path: Path, quality: int, radius: float, percent: int) -> None:
    height = round(image.height * (width / image.width))
    output = image.resize((width, height), Image.Resampling.LANCZOS)
    output = output.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=3))
    output.save(path, format="WEBP", quality=quality, method=6)
    with Image.open(path) as verified:
        assert verified.size == (width, height), (path, verified.size)
    print(f"{path}: {width}x{height}; {path.stat().st_size / 1024:.0f} KiB")

# Use the optimized, sharper 2880px render for the existing on-site hero.webp.
# Replacing the asset in place preserves Firebase, React, portal, and admin code.
enhance(2880, live, 88, 1.15, 93)
# Retain a 7680px wide 8K export for further artwork or future formats.
enhance(7680, master, 94, 1.8, 85)
# Keep a smaller responsive asset ready for mobile optimisation.
enhance(1280, mobile, 86, 0.95, 96)

print(f"Original preserved: {source} ({source.stat().st_size / 1024:.0f} KiB)")
