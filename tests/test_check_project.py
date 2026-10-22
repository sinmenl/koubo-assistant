"""Regression tests for actual project validation failures, using temporary files."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_project.py"
SPEC = importlib.util.spec_from_file_location("check_project", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class ProjectCheckTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        for relative in checker.ROUTE_FILES:
            self.write(relative, "# 功能\n")
        self.write("dependencies.md", "# 可选依赖\n")
        self.write("AGENTS.md", "\n".join(checker.ROUTE_FILES) + "\ndependencies.md\n")
        for name in checker.SKILL_NAMES:
            self.write(f"skills/{name}/SKILL.md", f"---\nname: {name}\ndescription: 示例\n---\n# 功能\n")
        self.write("VERSION", "0.2.0\n")
        self.write("CHANGELOG.md", "# 更新\n\n## [0.2.0] - 2026-10-22\n\n初次项目化。\n")
        self.write("config.example.json", json.dumps({"profile_id": "", "record_sessions": False,
                   "learn_style": False, "timezone": "Asia/Shanghai"}))
        self.write(".gitignore", "/local/\n/inbox/\n/output/\n/backups/\n.env\n.env.*\n"
                   "/memory/*\n!/memory/_README.md\n!/memory/_template.md\n"
                   "/style-profiles/*\n!/style-profiles/_template.md\n"
                   "/skills/dbskill/\n口播助手-进阶指令.jpg\n")

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self, tracked=False):
        errors, _ = checker.validate(self.root, tracked=tracked)
        return errors

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args],
                              capture_output=True, text=True, check=True)

    def test_minimal_project_passes(self):
        self.assertEqual(self.check(), [])

    def test_missing_link_is_rejected(self):
        self.write("README.md", "[打不开的说明](docs/missing.md)\n")
        self.assertTrue(any("链接目标不存在" in error for error in self.check()))

    def test_link_with_spaces_and_reference_link(self):
        self.write("docs/使用 说明.md", "# 说明\n")
        self.write("README.md", "[使用](<docs/使用 说明.md>)\n[说明][ref]\n\n[ref]: docs/missing.md\n")
        errors = self.check()
        self.assertEqual(sum("链接目标不存在" in error for error in errors), 1)

    def test_unclosed_fence_is_rejected(self):
        self.write("README.md", "# 使用\n\n```markdown\n未闭合\n")
        self.assertTrue(any("代码围栏未闭合" in error for error in self.check()))

    def test_fenced_examples_do_not_create_false_links(self):
        self.write("README.md", "````markdown\n[示例](does-not-exist.md)\n```\n````\n")
        self.assertEqual(self.check(), [])

    def test_route_and_skill_name_failures_are_rejected(self):
        (self.root / checker.ROUTE_FILES[0]).unlink()
        self.write("skills/linggan/SKILL.md", "---\nname: other-name\n---\n")
        errors = self.check()
        self.assertTrue(any("路由目标不存在" in error for error in errors))
        self.assertTrue(any("name 应与目录一致" in error for error in errors))

    def test_version_and_private_defaults_are_rejected(self):
        self.write("VERSION", "0.3.0\n")
        self.write("config.example.json", json.dumps({"profile_id": "alice", "record_sessions": True,
                   "learn_style": True, "timezone": "Asia/Shanghai"}))
        errors = self.check()
        self.assertTrue(any("最新版本不一致" in error for error in errors))
        self.assertTrue(any("profile_id 默认" in error for error in errors))
        self.assertEqual(sum("默认必须为 false" in error for error in errors), 2)

    def test_optional_dependency_and_private_material_are_not_scanned(self):
        self.write("skills/dbskill/README.md", "[旧依赖](missing.md)\n```\n")
        self.write("local/diary.md", "[私人](missing.md)\n```\n")
        self.assertEqual(self.check(), [])

    def test_uninitialized_repo_reports_tracked_skip(self):
        errors, notes = checker.validate(self.root, tracked=True)
        self.assertEqual(errors, [])
        self.assertTrue(any("已跳过" in note for note in notes))

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_tracked_private_file_is_rejected_even_when_ignored(self):
        self.git("init", "--quiet")
        self.write("local/diary.md", "私人记录\n")
        self.git("add", "-f", "local/diary.md")
        self.assertTrue(any("禁止提交" in error and "local/diary.md" in error for error in self.check(True)))

    @unittest.skipUnless(shutil.which("git"), "Git unavailable")
    def test_ignore_rules_protect_all_private_probes(self):
        self.git("init", "--quiet")
        self.assertEqual(self.check(True), [])
        self.write(".gitignore", "# missing rules\n")
        errors = self.check(True)
        self.assertEqual(sum("忽略规则未保护" in error for error in errors), len(checker.IGNORE_PROBES))

    def test_private_path_classification_keeps_only_templates(self):
        for relative in ("memory/alice.md", "style-profiles/alice.md", "inbox/entry.md",
                         "output/final.md", "backups/AGENTS.md", ".env.local",
                         "skills/dbskill/LICENSE", "AGENTS.md.bak-20261022",
                         "口播助手-进阶指令.jpg"):
            with self.subTest(relative=relative):
                self.assertTrue(checker.private_path(relative))
        for relative in ("memory/_template.md", "style-profiles/_template.md", "README.md"):
            with self.subTest(relative=relative):
                self.assertFalse(checker.private_path(relative))


if __name__ == "__main__":
    unittest.main()
