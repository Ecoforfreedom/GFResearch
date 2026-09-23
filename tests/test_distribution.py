"""Check actual package layouts, full instruction inclusion, and reproducibility."""

import hashlib
import importlib.util
import io
from pathlib import Path
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/build_distribution.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = BUILD.artifacts(ROOT)

    def test_platform_layouts_and_identical_payloads(self):
        for platform, prefix in (("claude", "gao-feng-research/"), ("bailian", "")):
            with self.subTest(platform=platform):
                with ZipFile(io.BytesIO(self.outputs[f"gao-feng-research-{platform}.zip"])) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(set(archive.namelist()), {prefix + item for item in BUILD.PACKAGE_FILES})
                    for item in BUILD.PACKAGE_FILES:
                        self.assertEqual(archive.read(prefix + item), BUILD.read_source(ROOT, item))

    def test_complete_instructions_are_embedded(self):
        portable = self.outputs["Gao-Feng-Research-Instructions.md"].decode("utf-8")
        texts = [BUILD.without_frontmatter(BUILD.read_source(ROOT, "SKILL.md").decode("utf-8"))]
        texts += [BUILD.read_source(ROOT, path).decode("utf-8").strip() for path in BUILD.REFERENCES]
        for text in texts:
            for path in BUILD.REFERENCES:
                text = text.replace(f"]({path})", f"](#{Path(path).stem})")
            self.assertIn(text, portable)
        self.assertNotIn("](references/", portable)

    def test_reproducible_and_distribution_current(self):
        self.assertEqual(self.outputs, BUILD.artifacts(ROOT))
        for name, data in self.outputs.items():
            self.assertEqual((ROOT / "dist" / name).read_bytes(), data)

    def test_checksums_and_upload_size(self):
        for line in self.outputs["SHA256SUMS.txt"].decode("ascii").splitlines():
            digest, name = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256(self.outputs[name]).hexdigest())
        self.assertLess(len(self.outputs["gao-feng-research-bailian.zip"]), 10_000_000)

    def test_references_and_entrypoint_metadata(self):
        text = BUILD.read_source(ROOT, "SKILL.md").decode("utf-8")
        meta = text.split("---\n", 2)[1]
        description = next(line for line in meta.splitlines() if line.startswith("description:")).split(":", 1)[1].strip().strip('"')
        self.assertLessEqual(len(description), 200)
        for path in BUILD.REFERENCES:
            self.assertTrue((ROOT / path).is_file())
            self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
