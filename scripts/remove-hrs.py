#!/usr/bin/env python3
"""
h2/h3 제목 앞의 불필요한 수평선(---)을 제거한다.
- frontmatter 구분자(파일 최상단 --- ... ---)는 보존
- 제목이 아닌 요소(::: tip 등) 앞의 ---는 보존
사용법: python3 scripts/remove-hrs.py docs
"""

import re
import sys
from pathlib import Path


def process(filepath: Path) -> bool:
    lines = filepath.read_text(encoding="utf-8").split("\n")
    n = len(lines)
    result = []
    i = 0

    # Preserve frontmatter block as-is
    if lines and lines[0].strip() == "---":
        result.append(lines[0])
        i = 1
        while i < n:
            result.append(lines[i])
            if lines[i].strip() == "---":
                i += 1
                break
            i += 1

    while i < n:
        line = lines[i]
        if line.strip() == "---":
            # Find next non-blank line
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            # Remove HR if it precedes a heading
            if j < n and re.match(r"^#{2,}\s", lines[j]):
                # Drop the HR and collapse surrounding blanks to one
                while result and result[-1].strip() == "":
                    result.pop()
                result.append("")
                i += 1
                while i < n and lines[i].strip() == "":
                    i += 1
                continue
        result.append(line)
        i += 1

    new_content = "\n".join(result)
    old_content = "\n".join(lines)
    if new_content != old_content:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    changed = 0
    for md in sorted(docs_dir.rglob("*.md")):
        if ".vitepress" in str(md):
            continue
        if process(md):
            print(f"  cleaned: {md}")
            changed += 1
    print(f"\nDone: {changed} file(s) cleaned.")


if __name__ == "__main__":
    main()
