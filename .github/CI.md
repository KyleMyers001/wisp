# Wisp CI

`.github/workflows/integrate.yaml` runs the same checks and mobile builds for
pull requests, pushes to `main`, merge queues, and manual dispatches. It uses the
Flutter version in `.fvmrc`, read-only repository permissions, immutable action
revisions, per-job timeouts, and cancellation of superseded runs.

## Jobs

- **Analysis and tests**: workflow/branding regression checks, deterministic icon
  regeneration (decoded pixels, not platform-dependent PNG compression), REUSE
  license metadata, lockfile consistency, Dart formatting,
  Flutter analysis, and the Flutter test suite. The test job explicitly builds
  the version of Vodozemac pinned in `pubspec.lock` before loading the native
  encryption fixture and downloads the screenshot fonts.
- **Android debug APK (ARM64)**: an ordinary debug build using the pinned Flutter
  SDK's supported compile SDK, without Firebase setup,
  store credentials, or production signing. The APK is available as the
  `wisp-android-debug-arm64` run artifact for seven days.
- **iOS simulator app (ARM64, unsigned)**: a simulator-only build without signing
  credentials, using Xcode 26.3 and Swift Package Manager on an ARM64 runner. The ZIP is
  available as `wisp-ios-simulator-arm64` for seven days. It cannot be installed
  on a physical iPhone.

Build artifacts are attached to the workflow run under the repository's Actions
page. CI does not deploy a website, upload to an app store, publish a container,
change application identifiers, or send Matrix notifications. A green build is
not physical-device or notification-delivery acceptance.

## Upstream automation

The inherited deployment, release, Matrix notification, and Flutter-update
workflows are preserved in `.github/upstream-workflows/` for reference. GitHub
Actions does not execute workflows from that directory. They target upstream
services or require upstream secrets and must be deliberately redesigned before
being enabled for Wisp. Do not copy them back merely to get a build.

The separate stale-issue workflow is unchanged. Desktop, web, device signing,
store publication, and emulator integration-test infrastructure are not part of
this initial mobile CI pipeline.

## Local workflow contract check

```sh
uv run --with pyyaml==6.0.3 python -m unittest discover -s scripts -p test_ci_workflow.py -v
```

Run `actionlint .github/workflows/integrate.yaml` to validate GitHub Actions
syntax and expressions. A manual run may be dispatched on the CI branch for
validation before merging; automatic `main` runs begin after this workflow is
merged into `main`.
