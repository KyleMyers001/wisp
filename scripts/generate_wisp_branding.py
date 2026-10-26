#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kyle Myers
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Regenerate Wisp icons: uv run --with pillow==12.0.0 python scripts/generate_wisp_branding.py."""

import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = (38, 19, 134)
BACKGROUND_TOP = (124, 103, 228)
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def generate_ios_icons(root: Path, artwork: Image.Image) -> list[Path]:
    catalog = root / "ios/Runner/Assets.xcassets/AppIcon.appiconset"
    entries = json.loads((catalog / "Contents.json").read_text())["images"]
    generated = set()
    for entry in entries:
        points = float(entry["size"].split("x")[0])
        scale = int(entry["scale"].removesuffix("x"))
        size = round(points * scale)
        output = catalog / entry["filename"]
        artwork.resize((size, size), Image.Resampling.LANCZOS).save(output)
        generated.add(output)
    return sorted(generated)


def transparent_mark(root: Path) -> Image.Image:
    # Keep the approved silhouette explicitly; purple cannot use teal color-keying.
    with Image.open(root / "assets/branding/wisp/classic-violet-mark.png") as source:
        return source.convert("RGBA")


def gradient_background(size: int) -> Image.Image:
    column = Image.new("RGB", (1, size))
    column.putdata([
        tuple(round(top + (bottom - top) * y / (size - 1))
              for top, bottom in zip(BACKGROUND_TOP, BACKGROUND))
        for y in range(size)
    ])
    return column.resize((size, size))


def centered_mark(mark: Image.Image, size: int, content_size: int) -> Image.Image:
    bounds = mark.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("The Wisp source artwork has no visible mark")
    alpha = ImageOps.contain(
        mark.getchannel("A").crop(bounds),
        (content_size, content_size),
        Image.Resampling.LANCZOS,
    )
    # Resample coverage alone so Lanczos cannot shift the flat mark color.
    content = Image.new("RGBA", alpha.size, mark.getpixel((0, 0)))
    content.putalpha(alpha)
    canvas = Image.new("RGBA", (size, size))
    canvas.alpha_composite(
        content, ((size - content.width) // 2, (size - content.height) // 2)
    )
    return canvas


def monochrome(mark: Image.Image) -> Image.Image:
    result = Image.new("RGBA", mark.size, "white")
    result.putalpha(mark.getchannel("A"))
    return result


def generate_android_icons(root: Path, artwork: Image.Image) -> list[Path]:
    res = root / "android/app/src/main/res"
    mark = transparent_mark(root)
    generated = []
    for density, scale in DENSITIES.items():
        size = round(48 * scale)
        layer_size = round(108 * scale)
        layer = centered_mark(mark, layer_size, round(64 * scale))
        notification_size = round(24 * scale)
        outputs = {
            res / f"mipmap-{density}/ic_launcher.png": artwork.resize(
                (size, size), Image.Resampling.LANCZOS
            ),
            res / f"drawable-{density}/ic_launcher_background.png": gradient_background(layer_size),
            res / f"drawable-{density}/ic_launcher_foreground.png": layer,
            res / f"drawable-{density}/ic_launcher_monochrome.png": monochrome(layer),
            res / f"drawable-{density}/notifications_icon.png": monochrome(
                centered_mark(mark, notification_size, round(20 * scale))
            ),
        }
        for path, image in outputs.items():
            image.save(path)
            generated.append(path)
    return generated


def generate_launch_and_in_app_artwork(root: Path, artwork: Image.Image) -> list[Path]:
    mark = transparent_mark(root)
    outputs = {
        root / "assets/logo/mini/logo_mini.png": artwork.resize(
            (500, 500), Image.Resampling.LANCZOS
        ),
        root / "assets/logo/mini/logo_mono_mini.png": monochrome(
            mark.resize((500, 500), Image.Resampling.LANCZOS)
        ),
    }
    for scale in (1, 2, 3):
        suffix = "" if scale == 1 else f"@{scale}x"
        path = (
            root
            / f"ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage{suffix}.png"
        )
        size = 168 * scale
        outputs[path] = mark.resize((size, size), Image.Resampling.LANCZOS)
    res = root / "android/app/src/main/res"
    for density, scale in DENSITIES.items():
        size = round(177 * scale)
        outputs[res / f"drawable-{density}/splash.png"] = mark.resize(
            (size, size), Image.Resampling.LANCZOS
        )
    for folder in ("drawable", "drawable-v21", "drawable-night", "drawable-night-v21"):
        outputs[res / folder / "background.png"] = Image.new("RGB", (1, 1), BACKGROUND)
    for path, image in outputs.items():
        image.save(path)
    return sorted(outputs)


def main() -> None:
    with Image.open(ROOT / "assets/branding/wisp/classic-violet.png") as source:
        artwork = source.convert("RGB")
    generated = generate_ios_icons(ROOT, artwork)
    generated += generate_android_icons(ROOT, artwork)
    generated += generate_launch_and_in_app_artwork(ROOT, artwork)
    print(f"Generated {len(generated)} Wisp PNG assets.")


if __name__ == "__main__":
    main()
