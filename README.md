# szuthesis Codex Skill

用于创建、修改和编译深圳大学本科毕业论文的 Codex skill。LaTeX 模板参考
[`liuchengxu/szuthesis`](https://github.com/liuchengxu/szuthesis)，已移除原作者的姓名、学号和论文正文，保留封面、诚信声明、页眉、中英文摘要、参考文献与页码结构。

## 安装

把本仓库克隆为 Codex 的 `szuthesis` skill：

```bash
git clone https://github.com/CooperArch/-.git "$HOME/.codex/skills/szuthesis"
```

Windows PowerShell：

```powershell
git clone https://github.com/CooperArch/-.git "$env:USERPROFILE\.codex\skills\szuthesis"
```

安装后可显式使用 `$szuthesis`。

## 新建论文工程

```bash
python scripts/new_thesis.py --output thesis \
  --title "论文题目" --title-en "English Title" \
  --author "姓名" --student-id "学号" --major "专业" \
  --college "学院" --advisor "指导教师" --advisor-title "职称" \
  --date "2026年4月27日" \
  --keywords-cn "关键词一；关键词二" \
  --keywords-en "keyword one; keyword two" \
  --chapter "绪论" --chapter "相关工作" --chapter "结论"
```

个人信息集中写入 `data/meta.tex`，并同步用于封面、诚信声明、页眉和中英文摘要。生成后需替换正文中的 `【待填写：…】`。

## 编译

需要 XeLaTeX、BibTeX 和 CTeX 中文字体支持，建议安装 TeX Live 2019 或更新版本。

```bash
python scripts/build_thesis.py thesis
python scripts/build_thesis.py thesis --strict
```

脚本优先使用 `latexmk -xelatex`，否则执行 `xelatex → bibtex → xelatex → xelatex`，并检查未定义引用、缺失字体和 LaTeX 错误。

## 格式提醒

上游示例成文于 2016 年。本仓库是可编译的工程骨架，不保证自动满足学校当前最新格式规范；提交前应以学校当期要求和学院通知为准。

模板来源与授权说明见 [NOTICE.md](NOTICE.md)。
