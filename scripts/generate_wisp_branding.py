#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Kyle Myers
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Regenerate Wisp icons: uv run --with pillow==12.0.0 python scripts/generate_wisp_branding.py."""

import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = (3, 57, 69)
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


def transparent_mark(artwork: Image.Image) -> Image.Image:
    # The supplied JPEG has a dark teal background; separate its bright mint mark.
    levels = [round(max(0, min(1, (value - 80) / 100)) * 255) for value in range(256)]
    alpha = artwork.getchannel("G").point(levels)
    mark = Image.new("RGBA", artwork.size, (98, 218, 176, 255))
    mark.putalpha(alpha)
    return mark


def centered_mark(mark: Image.Image, size: int, content_size: int) -> Image.Image:
    bounds = mark.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("The Wisp source artwork has no visible mark")
    content = ImageOps.contain(
        mark.crop(bounds), (content_size, content_size), Image.Resampling.LANCZOS
    )
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
    mark = transparent_mark(artwork)
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
            res / f"drawable-{density}/ic_launcher_background.png": Image.new(
                "RGB", (layer_size, layer_size), BACKGROUND
            ),
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
    outputs = {
        root / "assets/logo/mini/logo_mini.png": artwork.resize(
            (500, 500), Image.Resampling.LANCZOS
        ),
        root / "assets/logo/mini/logo_mono_mini.png": monochrome(
            transparent_mark(artwork).resize((500, 500), Image.Resampling.LANCZOS)
        ),
    }
    for scale in (1, 2, 3):
        suffix = "" if scale == 1 else f"@{scale}x"
        path = (
            root
            / f"ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage{suffix}.png"
        )
        size = 168 * scale
        outputs[path] = artwork.resize((size, size), Image.Resampling.LANCZOS)
    res = root / "android/app/src/main/res"
    for density, scale in DENSITIES.items():
        size = round(177 * scale)
        outputs[res / f"drawable-{density}/splash.png"] = artwork.resize(
            (size, size), Image.Resampling.LANCZOS
        )
    for folder in ("drawable", "drawable-v21", "drawable-night", "drawable-night-v21"):
        outputs[res / folder / "background.png"] = Image.new("RGB", (1, 1), BACKGROUND)
    for path, image in outputs.items():
        image.save(path)
    return sorted(outputs)


def main() -> None:
    with Image.open(ROOT / "assets/branding/wisp/logo.jpg") as source:
        artwork = source.convert("RGB")
    generated = generate_ios_icons(ROOT, artwork)
    generated += generate_android_icons(ROOT, artwork)
    generated += generate_launch_and_in_app_artwork(ROOT, artwork)
    print(f"Generated {len(generated)} Wisp PNG assets.")


if __name__ == "__main__":
    main()
