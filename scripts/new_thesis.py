#!/usr/bin/env python3
"""Scaffold a szuthesis project from the bundled clean template."""

import argparse
import re
import shutil
import sys
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "assets" / "thesis-template"
TEXT_EXTENSIONS = {".tex", ".sty", ".bib", ".gitignore"}

LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_escape(value):
    return re.sub(
        r"[\\&%$#_{}~^]",
        lambda match: LATEX_ESCAPES[match.group(0)],
        value,
    )


def write_chapter(directory, number, heading):
    path = directory / f"chapter{number:02d}.tex"
    path.write_text(
        f"% Chapter {number}. Replace the placeholder body below.\n"
        f"\\section{{{latex_escape(heading)}}}\n\n"
        "【待填写：正文内容】\n",
        encoding="utf-8",
    )


def replace_tokens(root, values):
    token_pattern = re.compile(r"@@([A-Z0-9_]+)@@")
    remaining = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8")
        text = token_pattern.sub(
            lambda match: values.get(match.group(1), match.group(0)),
            text,
        )
        for match in token_pattern.finditer(text):
            remaining.append(f"{path}: @@{match.group(1)}@@")
        path.write_text(text, encoding="utf-8")
    return remaining


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scaffold a new szuthesis XeLaTeX project from the bundled template."
    )
    parser.add_argument("--output", required=True, help="Destination directory")
    parser.add_argument("--title", default="【待填写：论文题目】")
    parser.add_argument("--title-en", default="【待填写：English Title】")
    parser.add_argument("--header-title", help="Short title for the running header (defaults to title)")
    parser.add_argument("--author", default="【待填写：姓名】")
    parser.add_argument("--student-id", default="【待填写：学号】")
    parser.add_argument("--major", default="【待填写：专业】")
    parser.add_argument("--college", default="【待填写：学院】")
    parser.add_argument("--advisor", default="【待填写：指导教师】")
    parser.add_argument("--advisor-title", default="【待填写：职称】")
    parser.add_argument("--date", default="【待填写：日期】")
    parser.add_argument("--keywords-cn", default="【待填写：中文关键词】")
    parser.add_argument("--keywords-en", default="【待填写：English Keywords】")
    parser.add_argument(
        "--chapter",
        action="append",
        default=[],
        help="Chapter heading; repeat for multiple chapters",
    )
    args = parser.parse_args(argv)

    if not TEMPLATE_DIR.is_dir():
        print(f"[ERROR] Missing template directory: {TEMPLATE_DIR}")
        return 1

    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        print(f"[ERROR] Output directory is not empty: {output}")
        return 1

    shutil.copytree(TEMPLATE_DIR, output, dirs_exist_ok=True)

    chapters = args.chapter or ["章节标题待定"]
    for number, heading in enumerate(chapters, start=1):
        write_chapter(output / "data", number, heading)

    header_title = args.header_title or args.title
    values = {
        "TITLE": latex_escape(args.title),
        "TITLE_EN": latex_escape(args.title_en),
        "HEADER_TITLE": latex_escape(header_title),
        "AUTHOR": latex_escape(args.author),
        "STUDENT_ID": latex_escape(args.student_id),
        "MAJOR": latex_escape(args.major),
        "COLLEGE": latex_escape(args.college),
        "ADVISOR": latex_escape(args.advisor),
        "ADVISOR_TITLE": latex_escape(args.advisor_title),
        "DATE": latex_escape(args.date),
        "KEYWORDS_ZH": latex_escape(args.keywords_cn),
        "KEYWORDS_EN": latex_escape(args.keywords_en),
        "CHAPTER_INCLUDES": "".join(
            f"\\include{{data/chapter{number:02d}}}\n"
            for number in range(1, len(chapters) + 1)
        ).rstrip(),
    }

    remaining = replace_tokens(output, values)
    if remaining:
        print("[ERROR] The following tokens were not replaced:")
        for item in remaining:
            print(f"  {item}")
        return 1

    print(f"[OK] Created thesis project at {output}")
    print(f"[OK] Chapters: {len(chapters)}")
    print("[NOTE] Replace every 【待填写：…】 marker before delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
