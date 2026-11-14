# 工程结构与同步点

`assets/thesis-template/` 生成的工程目录如下：

```text
.
|-- main.tex              # 文档类与页面顺序，\include 各章
|-- szutils.sty           # 宏包、页眉页脚、目录样式、图形路径
|-- data/
|   |-- meta.tex          # 全部个人信息宏（唯一数据源）
|   |-- cover.tex         # 封面
|   |-- statement.tex     # 诚信声明
|   |-- cnabstract.tex    # 中文摘要 + 关键词
|   |-- enabstract.tex    # 英文摘要 + 关键词 + lastpage 标签
|   |-- acknowledgement.tex
|   `-- chapterNN.tex     # 正文章节
|-- ref/references.bib
|-- graphics/             # 图片（含 szu.jpg 校徽）
`-- .gitignore
```

## 一处信息、多处同步

个人信息只定义在 `data/meta.tex`，不要在各页里直接改写姓名/题目。覆盖这些宏即同步全篇：

| 信息 | 宏 | 被引用位置 |
|---|---|---|
| 中文题目 | `\ThesisTitle` | 封面、诚信声明、中文摘要标题 |
| 英文题目 | `\ThesisTitleEn` | 英文摘要标题 |
| 页眉短题 | `\ThesisHeaderTitle` | `szutils.sty` 的 `\chead` |
| 姓名 | `\ThesisAuthor` | 封面、诚信声明、中文摘要署名 |
| 学号 | `\ThesisStudentId` | 封面、中文摘要 |
| 专业 / 学院 | `\ThesisMajor` / `\ThesisCollege` | 封面、中文摘要 |
| 指导教师 / 职称 | `\ThesisAdvisor` / `\ThesisAdvisorTitle` | 封面、英文摘要 |
| 日期 | `\ThesisDate` | 封面 |
| 关键词 | `\ThesisKeywordsZh` / `\ThesisKeywordsEn` | 中英文摘要 |

直接改上游原仓库时没有 `meta.tex`，等价位置是：封面 `data/cover.tex`、页眉 `szutils.sty` 的 `\chead` 那一行、声明 `data/statement.tex`、中文摘要 `data/cnabstract.tex`、英文摘要 `data/enabstract.tex`。上游原仓库还把所有个人信息硬编码在上述文件里，改题目/姓名时必须逐处替换，否则会出现封面、页眉、摘要标题不一致。

## 必须保留的格式约定

- `\documentclass[a4paper,punct,space,fancyhdr,fntef,UTF8]{ctexart}`；一级标题是 `\section`。
- 页面顺序固定：封面 → 诚信声明 → 目录 → 中文摘要 → 正文各章 → 参考文献 → 致谢 → 英文摘要。
- 正文页码 `\setcounter{page}{0}` 后从 1 重新计；页脚写“第 X 页 共 Y 页”，Y 来自 `data/enabstract.tex` 末尾的 `\label{lastpage}`。英文摘要不在最后一页时总页数会错。
- `szutils.sty` 里 `\DeclareGraphicsExtensions{.eps,.ps,.png,.jpg}` 和 `\graphicspath{{graphics/}}`：图放 `graphics/`，`\includegraphics{filename}` 不带扩展名。
- 参考文献用 `\bibliographystyle{plain}` + `\bibliography{ref/references}`；bib 文件名与 `main.tex` 一致。
- 中文字体由 `ctex` 与系统字体提供：XeLaTeX 下缺字体时会报“Font ... not found”，先查字体再改 `\setCJKmainfont`。

## 编译顺序

`latexmk -xelatex main.tex`，或手动 `xelatex → bibtex → xelatex → xelatex`。BibTeX 以 `main` 为主名运行，引用未定义时需要再跑一遍。
