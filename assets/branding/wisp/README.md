<!--
SPDX-FileCopyrightText: 2026 Kyle Myers
SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Wisp mobile branding

`classic-violet.png` is the approved 1024 × 1024 Classic Violet Wisp artwork,
preserved byte-for-byte from the selected preview. Its pale mark uses the
original Wisp silhouette against FluffyChat-inspired violet (`#7c67e4` to
`#261386`), without adopting the upstream mascot.

`classic-violet-mark.png` stores that same pale mark and its alpha mask for
adaptive icons, launch screens, and monochrome assets. The mask preserves the
original JPEG-derived silhouette exactly; it is raster artwork, not a vector.
`logo.jpg` remains unchanged as the original teal/mint source and provenance.
Use these source files rather than editing individual generated sizes.

Regenerate the checked-in iOS, Android, and shared in-app PNGs from the repository
root with Python 3.10+ and [uv](https://docs.astral.sh/uv/):

```sh
uv run --with pillow==12.0.0 python scripts/generate_wisp_branding.py
uv run --with pillow==12.0.0 python -m unittest discover -s scripts -p test_wisp_branding.py -v
```

The iOS icons and Android legacy icons reproduce the approved Classic Violet
artwork. iOS icons are opaque RGB PNGs with no baked-in rounded corners.
Android adaptive icons use the pale transparent mark centered in the safe area
of a 108 dp layer over a violet gradient; a white alpha-mask version supplies
themed and notification icons. Native launch screens use the transparent pale
mark over solid deep violet (`#261386`), avoiding a rectangular icon plate.

The generator also updates the existing launch-screen images and the two shared
in-app logo assets used by login, onboarding, lock, empty-state, and About views.
The native iOS launch background and Android color fallback are configured in
`ios/Runner/Base.lproj/LaunchScreen.storyboard` and
`android/app/src/main/res/values/ic_launcher_background.xml`; the tests keep
these in the same violet palette.
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
