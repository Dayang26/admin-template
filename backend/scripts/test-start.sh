#! /usr/bin/env bash
set -e
set -x

# 自动切换到项目根目录并加载虚拟环境
cd "$(dirname "$0")/.."
export PATH="./.venv/bin:$PATH"

python app/tests_pre_start.py

bash scripts/test.sh "$@"
