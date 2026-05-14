# 用一个干净的基础镜像，强制重新拉取
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制文件
COPY . .

# 强制安装 Flask（加上 --force-reinstall 确保不使用缓存）
RUN pip install --no-cache-dir --force-reinstall flask

# 声明端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]
