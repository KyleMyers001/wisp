# SPDX-FileCopyrightText: 2026 Kyle Myers
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Run with: python3 -m unittest discover -s scripts -p test_wisp_branding.py."""

import json
import plistlib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


class MobileBrandingTests(unittest.TestCase):
    def test_launch_and_in_app_artwork_use_wisp(self):
        source = Image.open(ROOT / "assets/branding/wisp/logo.jpg").convert("RGB")
        mini = Image.open(ROOT / "assets/logo/mini/logo_mini.png").convert("RGB")
        expected = source.resize((500, 500), Image.Resampling.LANCZOS)
        self.assertIsNone(ImageChops.difference(mini, expected).getbbox())
        mono = Image.open(ROOT / "assets/logo/mini/logo_mono_mini.png")
        self.assertEqual(mono.mode, "RGBA")
        self.assertEqual(mono.getchannel("A").getextrema(), (0, 255))
        for scale in (1, 2, 3):
            suffix = "" if scale == 1 else f"@{scale}x"
            image = Image.open(
                ROOT
                / f"ios/Runner/Assets.xcassets/LaunchImage.imageset/LaunchImage{suffix}.png"
            ).convert("RGB")
            size = 168 * scale
            self.assertEqual(image.size, (size, size))
            expected = source.resize((size, size), Image.Resampling.LANCZOS)
            self.assertIsNone(ImageChops.difference(image, expected).getbbox())
        res = ROOT / "android/app/src/main/res"
        densities = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
        for density, scale in densities.items():
            splash = Image.open(res / f"drawable-{density}/splash.png").convert("RGB")
            self.assertEqual(splash.size, (round(177 * scale),) * 2)
            expected = source.resize(splash.size, Image.Resampling.LANCZOS)
            self.assertIsNone(ImageChops.difference(splash, expected).getbbox())
        for folder in (
            "drawable",
            "drawable-v21",
            "drawable-night",
            "drawable-night-v21",
        ):
            background = Image.open(res / folder / "background.png").convert("RGB")
            self.assertEqual(background.getpixel((0, 0)), (3, 57, 69))

    def test_android_icons_use_wisp_in_every_density(self):
        source = Image.open(ROOT / "assets/branding/wisp/logo.jpg").convert("RGB")
        res = ROOT / "android/app/src/main/res"
        densities = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
        for density, scale in densities.items():
            with self.subTest(density=density):
                size = round(48 * scale)
                legacy = Image.open(res / f"mipmap-{density}/ic_launcher.png")
                expected = source.resize((size, size), Image.Resampling.LANCZOS)
                self.assertEqual(legacy.mode, "RGB")
                self.assertIsNone(ImageChops.difference(legacy, expected).getbbox())
                foreground = Image.open(
                    res / f"drawable-{density}/ic_launcher_foreground.png"
                )
                mono = Image.open(
                    res / f"drawable-{density}/ic_launcher_monochrome.png"
                )
                self.assertEqual(foreground.size, (round(108 * scale),) * 2)
                self.assertEqual(foreground.mode, "RGBA")
                background = Image.open(
                    res / f"drawable-{density}/ic_launcher_background.png"
                ).convert("RGB")
                self.assertEqual(background.size, foreground.size)
                self.assertEqual(background.getextrema(), ((3, 3), (57, 57), (69, 69)))
                alpha = foreground.getchannel("A")
                self.assertEqual(alpha.getextrema(), (0, 255))
                bounds = alpha.getbbox()
                assert bounds is not None
                left, top, right, bottom = bounds
                self.assertGreaterEqual(left, round(21 * scale))
                self.assertGreaterEqual(top, round(21 * scale))
                self.assertLessEqual(right, round(87 * scale))
                self.assertLessEqual(bottom, round(87 * scale))
                self.assertEqual(mono.getchannel("A").tobytes(), alpha.tobytes())
                for channel in mono.convert("RGB").split():
                    self.assertEqual(channel.getextrema(), (255, 255))
                notification = Image.open(
                    res / f"drawable-{density}/notifications_icon.png"
                )
                self.assertEqual(notification.size, (round(24 * scale),) * 2)
                self.assertEqual(notification.getchannel("A").getextrema(), (0, 255))
                for channel in notification.convert("RGB").split():
                    self.assertEqual(channel.getextrema(), (255, 255))
        adaptive = ET.parse(res / "mipmap-anydpi-v26/ic_launcher.xml")
        foreground_element = adaptive.find("foreground")
        assert foreground_element is not None
        self.assertEqual(
            foreground_element.get(ANDROID + "drawable"),
            "@drawable/ic_launcher_foreground",
        )
        for tag, expected in (
            ("background", "@drawable/ic_launcher_background"),
            ("monochrome", "@drawable/ic_launcher_monochrome"),
        ):
            element = adaptive.find(tag)
            assert element is not None
            self.assertEqual(element.get(ANDROID + "drawable"), expected)
        self.assertFalse((res / "drawable/ic_launcher_foreground.xml").exists())
        self.assertFalse((res / "drawable/ic_launcher_monochrome.xml").exists())

    def test_ios_icons_use_the_approved_artwork(self):
        source = ROOT / "assets/branding/wisp/logo.jpg"
        self.assertTrue(source.is_file(), "Approved Wisp source artwork is missing")
        artwork = Image.open(source).convert("RGB")
        catalog = ROOT / "ios/Runner/Assets.xcassets/AppIcon.appiconset"
        entries = json.loads((catalog / "Contents.json").read_text())["images"]
        for entry in entries:
            with self.subTest(filename=entry["filename"]):
                points = float(entry["size"].split("x")[0])
                scale = int(entry["scale"].removesuffix("x"))
                size = round(points * scale)
                icon = Image.open(catalog / entry["filename"])
                self.assertEqual(icon.size, (size, size))
                self.assertEqual(icon.mode, "RGB", "iOS icons must be opaque")
                expected = artwork.resize((size, size), Image.Resampling.LANCZOS)
                self.assertIsNone(ImageChops.difference(icon, expected).getbbox())

    def test_visible_mobile_names_are_wisp(self):
        with (ROOT / "ios/Runner/Info.plist").open("rb") as stream:
            info = plistlib.load(stream)
        self.assertEqual(info["CFBundleDisplayName"], "Wisp")
        self.assertEqual(info["CFBundleName"], "Wisp")
        for key, value in info.items():
            if key.startswith("NS") and key.endswith("UsageDescription"):
                self.assertNotIn("FluffyChat", value)
        with (ROOT / "ios/FluffyChat Share/Info.plist").open("rb") as stream:
            share = plistlib.load(stream)
        self.assertEqual(share["CFBundleDisplayName"], "Wisp Share")
        manifest = ET.parse(ROOT / "android/app/src/main/AndroidManifest.xml")
        application = manifest.find("application")
        assert application is not None
        self.assertEqual(application.get(ANDROID + "label"), "Wisp")
        settings = (ROOT / "lib/config/setting_keys.dart").read_text()
        self.assertIn(
            "applicationName<String>('chat.fluffy.application_name', 'Wisp')",
            settings,
        )


if __name__ == "__main__":
    unittest.main()
