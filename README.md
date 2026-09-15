# 练习写一个五子棋 AI

用 Python + Tkinter 实现的五子棋，AI 使用极大极小搜索 + alpha-beta 剪枝。

## 环境要求

- [uv](https://docs.astral.sh/uv/)：首次 `uv sync` 时会自动下载并使用 Python 3.13（见 `.python-version`）
- Tkinter 由 uv 安装的 CPython 自带，无需额外安装

## 快速开始

```bash
uv sync           # 创建 .venv，安装项目与开发依赖
uv run gomoku     # 15x15 棋盘
uv run gomoku 7   # 7x7 棋盘
uv run gomoku -p  # 开启性能分析，结果写入 /tmp/gomoku/
```

等价入口：`uv run python -m gomoku`。

## 开发命令

```bash
uv run pytest         # 运行测试
uv run ruff check .   # 静态检查
uv run ruff format .  # 格式化
uv run mypy           # 类型检查（strict）
```

## 项目结构

- `gomoku/board.py`：不可变棋盘与落子规则
- `gomoku/score.py`：局面评估与极大极小搜索
- `gomoku/app.py`：应用控制器，串联 UI 事件、棋盘状态与后台 AI 计算
- `gomoku/ui.py`：Tkinter 界面
- `gomoku/tcl.py`：修正虚拟环境中 Tcl/Tk 库的查找路径
- `gomoku/__main__.py`：命令行入口（`main()`）
- `tests/`：pytest 测试（不依赖 Tkinter）

## TODO

- [ ] 界面优化
- [ ] 修复 AI
