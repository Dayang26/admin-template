#!/usr/bin/env bash

set -e
set -x

# 自动切换到项目根目录并加载虚拟环境
cd "$(dirname "$0")/.."
export PATH="./.venv/bin:$PATH"

mypy app
ty check app
ruff check app
ruff format app --check
