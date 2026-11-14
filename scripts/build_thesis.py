#!/usr/bin/env python3
"""Compile a szuthesis project and surface actionable LaTeX diagnostics."""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".tex", ".sty", ".bib"}
SAMPLE_TERMS = [
    "徐留成",
    "2012080173",
    "潘微科",
    "融合内容信息的单类协同过滤推荐算法研究",
]

FATAL_PATTERNS = [
    re.compile(r"^!"),
    re.compile(r"! LaTeX Error:"),
    re.compile(r"! Undefined control sequence"),
    re.compile(r"! Package .* Error:"),
    re.compile(r"File `.*' not found"),
    re.compile(r"Emergency stop"),
]

UNDEFINED_PATTERNS = [
    re.compile(r"LaTeX Warning: (?:There were undefined references)"),
    re.compile(r"Reference `[^`]+' on page \d+ undefined"),
    re.compile(r"Citation `[^`]+' undefined"),
]

RERUN_PATTERNS = [
    re.compile(r"Label\(s\) may have changed"),
    re.compile(r"Rerun to get cross-references right"),
    re.compile(r"There were undefined references"),
]

WARNING_PATTERNS = [
    re.compile(r"Overfull \\hbox"),
    re.compile(r"Underfull \\hbox"),
    re.compile(r"Overfull \\vbox"),
    re.compile(r"Underfull \\vbox"),
    re.compile(r"Missing character"),
]

FONT_PATTERNS = [
    re.compile(r"Font .* not found"),
    re.compile(r"Cannot find font"),
]


def run(cmd, cwd):
    print("$", " ".join(str(part) for part in cmd))
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    text = result.stdout.decode("utf-8", errors="replace")
    if result.returncode != 0 or len(text) > 8000:
        shown = text if result.returncode != 0 else text[-8000:]
    else:
        shown = text
    print(shown.rstrip())
    return result.returncode, text


def find_placeholders(project):
    hits = []
    for path in sorted(project.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "【待填写" in text:
            hits.append(str(path))
    return hits


def find_sample_terms(project):
    hits = []
    for path in sorted(project.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for term in SAMPLE_TERMS:
            if term in text:
                hits.append(f"{path}: {term}")
    return hits


def analyze(log_text):
    fatal = [line for line in log_text.splitlines() if any(p.search(line) for p in FATAL_PATTERNS)]
    undefined = [line for line in log_text.splitlines() if any(p.search(line) for p in UNDEFINED_PATTERNS)]
    rerun = [line for line in log_text.splitlines() if any(p.search(line) for p in RERUN_PATTERNS)]
    warnings = [line for line in log_text.splitlines() if any(p.search(line) for p in WARNING_PATTERNS)]
    fonts = [line for line in log_text.splitlines() if any(p.search(line) for p in FONT_PATTERNS)]
    return fatal, undefined, rerun, warnings, fonts


def report(fatal, undefined, rerun, warnings, fonts):
    problems = []
    for label, lines in (
        ("Fatal", fatal),
        ("Undefined reference/citation", undefined),
        ("Rerun warning", rerun),
        ("Missing font", fonts),
    ):
        if lines:
            problems.append(f"[FAIL] {label}:")
            problems.extend(f"  {line.strip()}" for line in lines[:10])
    if warnings:
        print("[WARN] Overfull/Underfull or missing character lines:")
        for line in warnings[:10]:
            print(f"  {line.strip()}")
        if len(warnings) > 10:
            print(f"  ... {len(warnings)} total")
    if problems:
        print("\n".join(problems))
    return bool(problems)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compile a szuthesis project and check the LaTeX log."
    )
    parser.add_argument("project", help="Project directory containing main.tex")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when placeholder or sample content remains",
    )
    args = parser.parse_args(argv)

    project = Path(args.project).expanduser().resolve()
    main_tex = project / "main.tex"
    if not main_tex.is_file():
        print(f"[ERROR] main.tex not found under {project}")
        return 1

    xelatex = shutil.which("xelatex")
    bibtex = shutil.which("bibtex")
    latexmk = shutil.which("latexmk")
    if xelatex is None and latexmk is None:
        print("[ERROR] Neither xelatex nor latexmk found. Install TeX Live (texlive >= 2019) first.")
        return 1

    returncodes = []
    if latexmk:
        code, text = run(
            [latexmk, "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "main.tex"],
            project,
        )
        returncodes.append(code)
    else:
        xelatex_cmd = [xelatex, "-synctex=1", "-interaction=nonstopmode", "-file-line-error", "main.tex"]
        for _ in range(2):
            code, text = run(xelatex_cmd, project)
            returncodes.append(code)
        if bibtex and (project / "main.aux").is_file():
            code, text = run([bibtex, "main"], project)
            returncodes.append(code)
        for _ in range(2):
            code, text = run(xelatex_cmd, project)
            returncodes.append(code)

    log_path = project / "main.log"
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    fatal, undefined, rerun, warnings, fonts = analyze(log_text)

    placeholders = find_placeholders(project)
    samples = find_sample_terms(project)
    if placeholders:
        print("[NOTE] Placeholder markers remain:")
        for path in placeholders:
            print(f"  {path}")
    if samples:
        print("[WARN] Upstream sample identity/content still present:")
        for item in samples:
            print(f"  {item}")

    failed = any(returncodes) or report(fatal, undefined, rerun, warnings, fonts)
    if args.strict and (placeholders or samples):
        failed = True
        print("[FAIL] Strict mode: placeholders or sample content must be removed.")

    pdf = project / "main.pdf"
    if pdf.is_file():
        print(f"[OK] PDF: {pdf}")
    else:
        print("[WARN] main.pdf was not produced.")
        failed = True

    print("PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
