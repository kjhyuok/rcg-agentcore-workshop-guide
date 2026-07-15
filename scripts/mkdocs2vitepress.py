#!/usr/bin/env python3
"""
MkDocs Material → VitePress 문법 변환 스크립트.

콘텐츠 텍스트는 그대로 유지하고, 마크업 문법만 변환한다:
- admonition (!!! type "title") → ::: type title ... :::
- collapsible (??? type "title") → ::: details title ... :::
- figure markdown / { width } → <img> 태그
- 타입 매핑 (MkDocs 전용 → VitePress 유효 타입)

사용법: python3 scripts/mkdocs2vitepress.py docs
"""

import re
import sys
from pathlib import Path

# MkDocs → VitePress 타입 매핑
# VitePress 유효 타입: tip, info, warning, danger, note, details
TYPE_MAP = {
    "tip": "tip",
    "note": "info",
    "info": "info",
    "warning": "warning",
    "danger": "danger",
    "bug": "danger",
    "failure": "danger",
    "error": "danger",
    "abstract": "info",
    "success": "tip",
    "example": "info",
    "question": "warning",
    "quote": "info",
}

# 접이식(details)은 타이틀 앞에 이모지를 추가하여 원래 의미 보존
EMOJI_MAP = {
    "abstract": "ℹ️",
    "success": "✅",
    "example": "\U0001f9ea",
    "question": "❓",
    "quote": "\U0001f4ac",
    "bug": "\U0001f41b",
    "failure": "❌",
    "error": "❌",
}


def convert_admonitions(content: str) -> str:
    """Convert MkDocs admonitions to VitePress containers."""
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Match !!! type "title" or !!! type
        admon_match = re.match(r'^(!{3}|[?]{3})\s+(\w+)\s*"?([^"]*)"?\s*$', line)
        if admon_match:
            marker = admon_match.group(1)
            admon_type = admon_match.group(2).lower()
            title = admon_match.group(3).strip()

            is_collapsible = marker == "???"
            vp_type = "details" if is_collapsible else TYPE_MAP.get(admon_type, "info")

            # Add emoji for non-standard types
            if admon_type in EMOJI_MAP and title:
                title = f"{EMOJI_MAP[admon_type]} {title}"
            elif admon_type in EMOJI_MAP and not title:
                title = f"{EMOJI_MAP[admon_type]} {admon_type.capitalize()}"

            # Collect indented body lines (4 spaces)
            i += 1
            body_lines = []
            while i < len(lines):
                if lines[i].startswith("    "):
                    body_lines.append(lines[i][4:])  # dedent
                elif lines[i].strip() == "":
                    # Empty line within admonition
                    if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                        body_lines.append("")
                    else:
                        break
                else:
                    break
                i += 1

            # Output VitePress container
            if title:
                result.append(f"::: {vp_type} {title}")
            else:
                result.append(f"::: {vp_type}")
            result.extend(body_lines)
            result.append(":::")
            result.append("")
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def convert_figures(content: str) -> str:
    """Convert MkDocs figure markdown to plain img tags."""
    # Pattern: <figure markdown> ... </figure>
    content = re.sub(
        r'<figure\s+markdown\s*>\s*',
        '<figure>\n',
        content,
    )

    # Pattern: ![alt](src){ width="XXX" } → <img src="..." alt="..." width="XXX">
    def img_with_width(match):
        alt = match.group(1)
        src = match.group(2)
        width = match.group(3)
        return f'<img src="{src}" alt="{alt}" width="{width}">'

    content = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)\{\s*width="?(\d+)"?\s*\}',
        img_with_width,
        content,
    )

    return content


def convert_file(filepath: Path) -> bool:
    """Convert a single markdown file. Returns True if changes were made."""
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Skip if already converted (has ::: containers)
    # But still process if has MkDocs syntax
    has_mkdocs = bool(re.search(r'^(!{3}|[?]{3})\s+\w+', content, re.MULTILINE))

    if has_mkdocs:
        content = convert_admonitions(content)

    if "{ width" in content or "figure markdown" in content:
        content = convert_figures(content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/mkdocs2vitepress.py <docs-dir>")
        sys.exit(1)

    docs_dir = Path(sys.argv[1])
    if not docs_dir.is_dir():
        print(f"Error: {docs_dir} is not a directory")
        sys.exit(1)

    converted = 0
    for md_file in sorted(docs_dir.rglob("*.md")):
        if ".vitepress" in str(md_file):
            continue
        if convert_file(md_file):
            print(f"  converted: {md_file}")
            converted += 1

    print(f"\nDone: {converted} file(s) converted.")


if __name__ == "__main__":
    main()
