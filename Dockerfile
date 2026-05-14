# 保留你项目原有的 Python 基础镜像逻辑，改成 Railway 兼容版
FROM python:3.11-slim

WORKDIR /app

# 复制项目所有文件
COPY . .

# 安装依赖（包含 requirements.txt 里的所有包，加 gunicorn 提升稳定性）
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 暴露端口（Railway 会自动映射）
EXPOSE $PORT

# 关键：适配 Railway 端口，用 gunicorn 启动 web_server.py
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT web_server:app"]
