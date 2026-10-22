#!/usr/bin/env python3
"""Validate the distributable agent project without external dependencies.

This checks repository structure and publication boundaries, not model behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROUTE_FILES = (
    "skills/jianxingying/cards.md",
    "skills/jianxingying/history.md",
    "skills/jianxingying/resonate.md",
    "skills/jianxingying/flow.md",
    "skills/jianxingying/title.md",
    "skills/jianxingying/linggan.md",
    "skills/jianxingying/review.md",
    "skills/short-video-diagnosis/SKILL.md",
    "skills/koubo-huzige/SKILL.md",
    "skills/jianxingying/troubleshooting.md",
)
SKILL_NAMES = ("linggan", "dongjian-card", "koubo-huzige", "short-video-diagnosis")
TEMPLATE_FILES = {"_README.md", "_template.md"}
PRIVATE_DIRS = {"local", "inbox", "output", "backups", "backup", ".backups"}
IGNORE_PROBES = (
    "local/config.json",
    "local/memory/alice.md",
    "inbox/material.md",
    "output/script.md",
    "backups/AGENTS.md",
    "memory/alice.md",
    "style-profiles/alice.md",
    ".env",
    ".env.local",
    "skills/dbskill/dbs/SKILL.md",
    "口播助手-进阶指令.jpg",
)


def private_path(relative: str) -> bool:
    """Return whether a tracked path is excluded from the distributable project."""
    parts = Path(relative).parts
    if not parts:
        return False
    if any(part in PRIVATE_DIRS for part in parts):
        return True
    if len(parts) >= 2 and parts[:2] == ("skills", "dbskill"):
        return True
    if parts[0] in {"memory", "style-profiles"}:
        return len(parts) != 2 or parts[-1] not in TEMPLATE_FILES
    if any(part == ".env" or part.startswith(".env.") for part in parts):
        return True
    if any(".bak-" in part or part.endswith((".bak", ".backup")) for part in parts):
        return True
    return parts[-1] == "口播助手-进阶指令.jpg"


def source_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if private_path(relative.as_posix()):
            continue
        yield path


def without_fences(text: str, label: str, errors: list[str]) -> str:
    """Remove fenced code and report any missing closing fence."""
    output = []
    fence_char = None
    fence_size = 0
    start_line = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_char is None:
            if match:
                fence_char = match.group(1)[0]
                fence_size = len(match.group(1))
                start_line = line_number
                output.append("")
            else:
                output.append(line)
        else:
            if (match and match.group(1)[0] == fence_char
                    and len(match.group(1)) >= fence_size
                    and not match.group(2).strip()):
                fence_char = None
            output.append("")
    if fence_char is not None:
        errors.append(f"{label}:{start_line}: 代码围栏未闭合")
    return "\n".join(output)


def link_targets(text: str):
    # Inline destinations, including <paths with spaces> and optional titles.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[^\n)]*)?\)", text):
        yield match.group(1).strip("<>")
    # Reference definitions: [label]: path; their targets must exist as well.
    for match in re.finditer(r"^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)", text, re.MULTILINE):
        yield match.group(1).strip("<>")


def check_markdown(root: Path, errors: list[str]) -> None:
    for path in source_markdown(root):
        label = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{label}: 无法读取 Markdown：{exc}")
            continue
        text = without_fences(text, label, errors)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        for destination in link_targets(text):
            parsed = urlsplit(destination)
            if parsed.scheme or destination.startswith("//"):
                continue
            target_name = unquote(parsed.path)
            if not target_name:
                continue
            target = (path.parent / target_name).resolve()
            if not target.is_relative_to(root):
                errors.append(f"{label}: 链接越出项目目录：{destination}")
            elif not target.exists():
                errors.append(f"{label}: 链接目标不存在：{destination}")


def check_routes(root: Path, errors: list[str]) -> None:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        errors.append("缺少 AGENTS.md")
        return
    text = agents.read_text(encoding="utf-8")
    for relative in ROUTE_FILES:
        if relative not in text:
            errors.append(f"AGENTS.md: 缺少功能路由：{relative}")
        if not (root / relative).is_file():
            errors.append(f"功能路由目标不存在：{relative}")
    dependency_refs = re.findall(r"(?:[\w.-]+/)*dependencies\.md", text)
    if not dependency_refs:
        errors.append("AGENTS.md: 缺少 dependencies.md 依赖说明入口")
    for relative in set(dependency_refs):
        if not (root / relative).is_file():
            errors.append(f"依赖说明入口不存在：{relative}")
    for name in SKILL_NAMES:
        relative = f"skills/{name}/SKILL.md"
        path = root / relative
        if not path.is_file():
            errors.append(f"缺少 Skill：{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
        if not frontmatter:
            errors.append(f"{relative}: 缺少 YAML frontmatter")
            continue
        found = re.search(r"^name:\s*([^\n]+?)\s*$", frontmatter.group(1), re.MULTILINE)
        actual = found.group(1).strip("\"'") if found else None
        if actual != name:
            errors.append(f"{relative}: name 应与目录一致（{name}），实际为 {actual!r}")


def check_metadata(root: Path, errors: list[str]) -> None:
    version_path = root / "VERSION"
    changelog_path = root / "CHANGELOG.md"
    if not version_path.is_file() or not changelog_path.is_file():
        errors.append("缺少 VERSION 或 CHANGELOG.md")
    else:
        version = version_path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append("VERSION 必须为 major.minor.patch 格式")
        releases = re.findall(r"^##\s+\[?(\d+\.\d+\.\d+)\]?(?:\s|$)",
                              changelog_path.read_text(encoding="utf-8"), re.MULTILINE)
        if not releases or releases[0] != version:
            errors.append("VERSION 与 CHANGELOG.md 最新版本不一致")
    config_path = root / "config.example.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"config.example.json 无法读取：{exc}")
        return
    if not isinstance(config, dict):
        errors.append("config.example.json 必须是 JSON 对象")
        return
    if config.get("profile_id") != "":
        errors.append("config.example.json: profile_id 默认必须为空字符串")
    for flag in ("record_sessions", "learn_style"):
        if config.get(flag) is not False:
            errors.append(f"config.example.json: {flag} 默认必须为 false")
    if not isinstance(config.get("timezone"), str) or not config["timezone"]:
        errors.append("config.example.json: 缺少 timezone")


def git_command(root: Path, *arguments: str, input_text: str | None = None):
    return subprocess.run(["git", "-C", str(root), *arguments], input=input_text,
                          text=True, capture_output=True, check=False)


def check_tracked(root: Path, errors: list[str], notes: list[str]) -> None:
    try:
        top = git_command(root, "rev-parse", "--show-toplevel")
    except FileNotFoundError:
        errors.append("--tracked 需要 Git，但本机未找到 git")
        return
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        notes.append("尚未在本项目根初始化 Git；已跳过 tracked/忽略规则检查。")
        return
    tracked = git_command(root, "ls-files", "-z")
    if tracked.returncode != 0:
        errors.append("git ls-files 失败：" + tracked.stderr.strip())
        return
    for relative in filter(None, tracked.stdout.split("\0")):
        if private_path(relative):
            errors.append(f"禁止提交个人资料、第三方副本或旧文件：{relative}")
    ignored = git_command(root, "check-ignore", "--no-index", "--stdin", "-z",
                          input_text="\0".join(IGNORE_PROBES) + "\0")
    if ignored.returncode not in (0, 1):
        errors.append("git check-ignore 失败：" + ignored.stderr.strip())
        return
    ignored_paths = set(filter(None, ignored.stdout.split("\0")))
    for relative in IGNORE_PROBES:
        if relative not in ignored_paths:
            errors.append(f"忽略规则未保护此路径：{relative}")


def validate(root: Path, tracked: bool = False) -> tuple[list[str], list[str]]:
    root = root.resolve()
    errors: list[str] = []
    notes: list[str] = []
    if not root.is_dir():
        return [f"项目目录不存在：{root}"], notes
    check_routes(root, errors)
    check_markdown(root, errors)
    check_metadata(root, errors)
    if tracked:
        check_tracked(root, errors, notes)
    return errors, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="项目根目录（默认是脚本所在项目）")
    parser.add_argument("--tracked", action="store_true", help="同时检查 Git 提交范围和忽略规则")
    args = parser.parse_args()
    errors, notes = validate(args.root, tracked=args.tracked)
    for note in notes:
        print("提示：", note)
    for error in errors:
        print("失败：", error)
    if errors:
        print(f"检查未通过：{len(errors)} 项。")
        return 1
    print("项目结构、引用、版本与默认配置检查通过。" + (" Git 范围检查已请求。" if args.tracked else ""))
    print("本检查不代表口播行为已通过模型实测。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
