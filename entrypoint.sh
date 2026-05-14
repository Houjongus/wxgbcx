#!/bin/bash
set -e

# 启动 Flask Web 服务
python /app/web_server.py &

# 保持容器运行
tail -f /dev/null
