<!--
SPDX-FileCopyrightText: 2019-Present Christian Kußowski
SPDX-FileCopyrightText: 2019-Present Contributors to FluffyChat

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Wisp

A personal Matrix client, designed with Hermes in mind.

Wisp is a personal fork of [FluffyChat](https://github.com/krille-chan/fluffychat),
built with [Flutter](https://flutter.dev) for the [Matrix](https://matrix.org)
network. This repository is the home for Wisp's branding and personal
customizations. Wisp is independent of the upstream FluffyChat project.

## Features

Wisp inherits FluffyChat's Matrix messaging features, including:

- Private and public group chats, channels, and Spaces
- Text messages, images, files, and voice messages
- Video calls with Matrix RTC
- End-to-end encryption, encrypted chat backup, and emoji verification
- Custom emotes, stickers, and Material You design
- Push notifications, location sharing, and group moderation

## Build from source

Use the Flutter version pinned in [`.fvmrc`](.fvmrc) and install
[Rust](https://www.rust-lang.org/tools/install). Platform-specific Flutter
build tooling is also required for your target device.

```sh
git clone https://github.com/KyleMyers001/wisp.git
cd wisp
flutter pub get
flutter run
```

These instructions build this fork. Upstream FluffyChat downloads are not Wisp
builds.

### Web

Before running or building for the web, prepare the web dependencies:

```sh
./scripts/prepare-web.sh
flutter run -d chrome
```

The preparation script uses additional tools, including `yq` and
`flutter_rust_bridge_codegen` (installed by the script). See
[`scripts/prepare-web.sh`](scripts/prepare-web.sh) for the preparation steps.

## Configuration

On the web, serve a `config.json` alongside Wisp. Start with
[`config.sample.json`](config.sample.json) and include only the settings you
want to override, such as `defaultHomeserver`.

The inherited app also supports Mobile Device Management (MDM) configuration on
Android and iOS. Android's supported restrictions are defined in
[`app_restrictions.xml`](android/app/src/main/res/xml/app_restrictions.xml).

## Integration tests

With Docker installed and running, prepare the test environment before each run:

```sh
./scripts/prepare_integration_test.sh
flutter test integration_test/mobile_test.dart
```

## Upstream and credits

Wisp builds on the work of Christian Kußowski and the
[FluffyChat contributors](https://github.com/krille-chan/fluffychat).
Upstream's [website](https://fluffychat.im),
[community](https://matrix.to/#/#fluffy-space:matrix.org), and
[translations](https://hosted.weblate.org/projects/fluffychat/) belong to
FluffyChat, not Wisp.

Thanks to Fabiyamada for the original FluffyChat logo and banner, to the
translators and testers, and to MTRNord, Sorunome, and Advocatux. The
[Matrix Foundation's emoji translations](https://github.com/matrix-org/matrix-spec/blob/main/data-definitions/sas-emoji.json)
used for verification are licensed under Apache 2.0.

## License

Wisp retains the upstream [AGPL-3.0-or-later license](LICENSE). Asset and
third-party license notices are preserved in the repository; see
[`REUSE.toml`](REUSE.toml) and [`LICENSES`](LICENSES).
