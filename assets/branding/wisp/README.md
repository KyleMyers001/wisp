<!--
SPDX-FileCopyrightText: 2026 Kyle Myers
SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Wisp mobile branding

`logo.jpg` is the original 1024 × 1024 Wisp artwork supplied for this fork.
Keep it as the source rather than editing individual generated sizes.

Regenerate the checked-in iOS, Android, and shared in-app PNGs from the repository
root with Python 3.10+ and [uv](https://docs.astral.sh/uv/):

```sh
uv run --with pillow==12.0.0 python scripts/generate_wisp_branding.py
uv run --with pillow==12.0.0 python -m unittest discover -s scripts -p test_wisp_branding.py -v
```

The iOS icons and Android legacy icons retain the supplied artwork, including its
teal background. iOS icons are opaque RGB PNGs with no baked-in rounded corners.
Android adaptive icons use a transparent mint rendition of the mark centered in
the safe area of a 108 dp layer; a white alpha-mask version supplies themed and
notification icons. These transparent renditions are derived from the supplied
JPEG, not a separate vector original.

The generator also updates the existing launch-screen images and the two shared
in-app logo assets used by login, onboarding, lock, empty-state, and About views.
Desktop launcher assets, the upstream banner/mascot, and store-listing artwork
are not regenerated here.

Do not use the inherited `flutter_launcher_icons` configuration in `pubspec.yaml`
to regenerate mobile icons: it still points to upstream artwork. Use the Wisp
generator above for mobile assets.

Names are set in `ios/Runner/Info.plist`, `ios/FluffyChat Share/Info.plist`,
`android/app/src/main/AndroidManifest.xml`, and the `applicationName` default in
`lib/config/setting_keys.dart`. Existing managed or saved overrides of that
setting still take precedence. The original settings keys, package and bundle
identifiers, URL schemes, app groups, push configuration, and signing settings
are unchanged. Installing Wisp alongside upstream FluffyChat requires a separate
identifier/signing change. Secure session-backup keys retain their original
FluffyChat namespace independently of the display name, so rebranding does not
strand existing recovery data or prevent its deletion on logout.

Source artwork and generated Wisp images are recorded separately from upstream
artwork in `REUSE.toml`, under the repository's AGPL-3.0-or-later license. Original
FluffyChat credits and notices remain in place for the retained upstream work.
