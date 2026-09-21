#!/usr/bin/env python3
"""Run: python -m unittest scripts.test_sync_agents_config -v"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sync_agents_config import copy_files, is_reparse_point, mirror_dir


class CopyFilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.src = self.tmp / "src"
        self.dst = self.tmp / "dst"
        self.src.mkdir()

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_copies_named_files_only(self) -> None:
        (self.src / "a.md").write_text("a")
        (self.src / "b.json").write_text("b")
        (self.src / "c.txt").write_text("c")

        copy_files(self.src, self.dst, ["a.md", "b.json"])

        self.assertEqual((self.dst / "a.md").read_text(), "a")
        self.assertEqual((self.dst / "b.json").read_text(), "b")
        self.assertFalse((self.dst / "c.txt").exists())

    def test_missing_named_file_skipped_not_errored(self) -> None:
        copy_files(self.src, self.dst, ["missing.md"])
        self.assertFalse((self.dst / "missing.md").exists())

    def test_missing_source_dir_is_noop(self) -> None:
        copy_files(self.src / "nope", self.dst, ["a.md"])
        self.assertFalse(self.dst.exists())

    def test_additive_leaves_unrelated_dst_files(self) -> None:
        self.dst.mkdir()
        (self.dst / "keepme.txt").write_text("keep")
        (self.src / "a.md").write_text("a")

        copy_files(self.src, self.dst, ["a.md"])

        self.assertEqual((self.dst / "keepme.txt").read_text(), "keep")


class MirrorDirTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.src = self.tmp / "src"
        self.dst = self.tmp / "dst"
        self.src.mkdir()

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_copies_nested_tree(self) -> None:
        (self.src / "sub").mkdir()
        (self.src / "sub" / "f.md").write_text("hello")

        mirror_dir(self.src, self.dst)

        self.assertEqual((self.dst / "sub" / "f.md").read_text(), "hello")

    def test_deletes_dst_extras_not_in_src(self) -> None:
        self.dst.mkdir()
        (self.dst / "stale.md").write_text("old")
        (self.dst / "stale_dir").mkdir()
        (self.dst / "stale_dir" / "x.txt").write_text("old")
        (self.src / "keep.md").write_text("new")

        mirror_dir(self.src, self.dst)

        self.assertFalse((self.dst / "stale.md").exists())
        self.assertFalse((self.dst / "stale_dir").exists())
        self.assertEqual((self.dst / "keep.md").read_text(), "new")

    def test_excludes_named_dir(self) -> None:
        (self.src / "synced").mkdir()
        (self.src / "synced" / "x.txt").write_text("x")
        (self.src / "real").mkdir()
        (self.src / "real" / "y.txt").write_text("y")

        mirror_dir(self.src, self.dst, exclude_dirs=frozenset({"synced"}))

        self.assertFalse((self.dst / "synced").exists())
        self.assertEqual((self.dst / "real" / "y.txt").read_text(), "y")

    def test_excludes_glob_pattern(self) -> None:
        (self.src / "foo-workspace").mkdir()
        (self.src / "foo-workspace" / "x.txt").write_text("x")
        (self.src / "keep").mkdir()

        mirror_dir(self.src, self.dst, exclude_globs=("*-workspace",))

        self.assertFalse((self.dst / "foo-workspace").exists())
        self.assertTrue((self.dst / "keep").exists())

    def test_skip_junctions_excludes_symlinked_dir(self) -> None:
        real_target = self.tmp / "real_target"
        real_target.mkdir()
        (real_target / "f.txt").write_text("f")
        link = self.src / "linked"
        try:
            link.symlink_to(real_target, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation requires elevated privileges on this host")

        mirror_dir(self.src, self.dst, skip_junctions=True)

        self.assertFalse((self.dst / "linked").exists())

    def test_skip_junctions_excludes_ntfs_junction(self) -> None:
        real_target = self.tmp / "real_target"
        real_target.mkdir()
        (real_target / "f.txt").write_text("f")
        junction = self.src / "junctioned"
        import subprocess

        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(real_target)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.skipTest(f"mklink /J unavailable: {result.stderr}")

        self.assertTrue(is_reparse_point(junction))
        mirror_dir(self.src, self.dst, skip_junctions=True)
        self.assertFalse((self.dst / "junctioned").exists())

    def test_missing_source_is_noop(self) -> None:
        mirror_dir(self.src / "nope", self.dst)
        self.assertFalse(self.dst.exists())

    def test_rerun_is_idempotent(self) -> None:
        (self.src / "f.md").write_text("v1")
        mirror_dir(self.src, self.dst)
        mirror_dir(self.src, self.dst)
        self.assertEqual((self.dst / "f.md").read_text(), "v1")


if __name__ == "__main__":
    unittest.main()
