#!/usr/bin/env bash

set -e
set -x

# 自动切换到项目根目录并加载虚拟环境
cd "$(dirname "$0")/.."
export PATH="./.venv/bin:$PATH"

coverage run -m pytest tests/
coverage report
coverage html --title "${1:-coverage}"
