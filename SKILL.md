---
name: szuthesis
description: Create, revise, and compile Shenzhen University undergraduate theses using the liuchengxu/szuthesis XeLaTeX/CTeX project. Use for 深圳大学本科毕业论文 or szuthesis LaTeX work: scaffolding a project, filling cover/statement/abstracts, writing chapters and bibliography, and producing a visually checked PDF. Do not use for unrelated LaTeX documents or for the repository's beamer defense slides.
---

# 深圳大学本科毕业论文（szuthesis）

基于 `liuchengxu/szuthesis`（上游 snapshot：commit `4a19b9d`）的深圳大学本科毕业论文写作与编译技能。上游例子成文于 2016 年，格式可能已不是学校最新要求；若用户给出当前官方模板或格式文件，以用户提供的内容为准，本技能提供的是可编译的 LaTeX 工程骨架。

## 两条工作流

**新建工程**：用 `scripts/new_thesis.py` 从 `assets/thesis-template/` 复制骨架，并把封面、诚信声明、页眉、中英文摘要、参考文献一次性填成用户信息。标题会经 LaTeX 转义，避免用户输入里的 `& % $ _ { }` 破坏排版。

```bash
python scripts/new_thesis.py --output <目标目录> \
  --title "论文题目" --title-en "English Title" \
  --author "姓名" --student-id "学号" --major "专业" \
  --college "学院" --advisor "指导教师" --advisor-title "职称" \
  --date "2026年4月27日" --keywords-cn "关键词一；关键词二" \
  --keywords-en "keyword one; keyword two" \
  --chapter "绪论" --chapter "相关工作" --chapter "结论"
```

`--chapter` 可重复；省略时只生成一个标题为“章节标题待定”的 `data/chapter01.tex`。生成后把正文里所有 `【待填写：…】` 替换为真实内容，不能带占位符交付。

**修改已有工程**（包括用户直接 clone 的上游仓库）：先读 [references/template-map.md](references/template-map.md)，按那里的“一处信息、多处同步”清单把封面、页眉、声明、中英文摘要一起改，不要只改一处。改动后照常编译并目检。

## 写作与结构约束

- 文档类是 `ctexart`，**没有 `\chapter`**：一级结构用 `\section`，二级 `\subsection`。章文件在 `data/` 下，由 `main.tex` 用 `\include` 引入。
- 页眉标题是 `szutils.sty` 里的 `\chead`，不要改 `main.tex` 就以为改完了页眉；模板用 `\ThesisHeaderTitle` 统一取值。
- 参考文献固定 `\bibliographystyle{plain}`，引用命令来自 `natbib`（`\citep`/`\citet`）。条目放在 `ref/references.bib`，不要另建 `.bib` 而不改 `main.tex`。
- 图片放进 `graphics/` 即可直接 `\includegraphics{name}`，`szutils.sty` 已设 `\graphicspath{{graphics/}}`；同名图片优先 `.eps .ps .png .jpg`。
- 只写用户提供的或用户明确要求整理的内容，不编造数据、实验、参考文献或结论。

## 编译

```bash
python scripts/build_thesis.py <工程目录>
```

脚本优先用 `latexmk -xelatex`，没有 latexmk 时回退为上游的手动三步：`xelatex → bibtex → xelatex → xelatex`。它只做编译和日志检查，不修改工程内容；未定义引用、缺失字体/宏包、`! LaTeX Error` 会按失败报告，Overfull/Underfull hbox 作为警告列出。交付前用 `--strict`，脚本会把 `【待填写：…】` 也当失败。

## 交付前自检

读 [references/qa-checklist.md](references/qa-checklist.md)，逐页渲染 PDF 检查封面、诚信声明、目录页码、页眉页脚、“第 X 页 共 Y 页”的总页数、参考文献、致谢与英文摘要的落位。`\pageref{lastpage}` 是模板末尾 `data/enabstract.tex` 里的手工标签，移动英文摘要位置时必须一起检查总页数显示。

修改脚本或模板时，先在 `work/` 下用新脚本生成一份工程并编译一次，确认 `main.pdf` 能出、占位符能替换、中文字体正常。
