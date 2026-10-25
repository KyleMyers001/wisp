# SPDX-FileCopyrightText: 2026 Kyle Myers
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Run with: uv run --with pyyaml==6.0.3 python -m unittest discover -s scripts -p test_ci_workflow.py."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_workflow(name):
    return yaml.load(
        (ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader
    )


class CIWorkflowTests(unittest.TestCase):
    def test_android_compile_sdk_follows_the_pinned_flutter_toolchain(self):
        gradle = (ROOT / "android/app/build.gradle.kts").read_text()
        self.assertIn("compileSdk = flutter.compileSdkVersion", gradle)

    def test_pr_and_main_use_the_same_secret_free_builds(self):
        workflow = load_workflow("integrate.yaml")
        events = workflow["on"]
        self.assertIn("pull_request", events)
        self.assertIn("push", events)
        self.assertEqual(events["push"]["branches"], ["main"])
        self.assertIn("workflow_dispatch", events)
        self.assertIn("merge_group", events)
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(set(workflow["jobs"]), {"checks", "android", "ios"})
        for name, job in workflow["jobs"].items():
            with self.subTest(job=name):
                self.assertIn("timeout-minutes", job)
                self.assertNotIn("continue-on-error", job)
                text = yaml.dump(job)
                self.assertNotIn("secrets.", text)
                self.assertNotIn("pull_request_target", text)
                self.assertIn("flutter-version-file: .fvmrc", text)
                for step in job["steps"]:
                    if "uses" in step:
                        self.assertRegex(step["uses"], r"^[\w-]+/[\w-]+@[0-9a-f]{40}$")
        for platform in ("android", "ios"):
            uploads = [
                step
                for step in workflow["jobs"][platform]["steps"]
                if step.get("uses", "").startswith("actions/upload-artifact@")
            ]
            self.assertEqual(len(uploads), 1)
            self.assertEqual(uploads[0]["with"]["if-no-files-found"], "error")
        android_commands = "\n".join(
            step.get("run", "") for step in workflow["jobs"]["android"]["steps"]
        )
        ios_commands = "\n".join(
            step.get("run", "") for step in workflow["jobs"]["ios"]["steps"]
        )
        self.assertIn("flutter build apk --debug", android_commands)
        self.assertIn("--no-codesign", ios_commands)
        self.assertIn("CODE_SIGNING_ALLOWED=NO", ios_commands)
        self.assertIn("ARCHS=arm64", ios_commands)

    def test_upstream_publishing_and_secret_driven_automation_are_archived(self):
        for name in (
            "main_deploy.yaml",
            "release.yaml",
            "matrix_notify.yaml",
            "flutter_update.yaml",
        ):
            with self.subTest(workflow=name):
                self.assertFalse((ROOT / ".github/workflows" / name).exists())
                self.assertTrue((ROOT / ".github/upstream-workflows" / name).is_file())


if __name__ == "__main__":
    unittest.main()
