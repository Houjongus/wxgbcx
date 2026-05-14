# 用一个通用的基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 把当前文件夹里的所有文件复制到镜像里
COPY . .

# 直接安装 Flask，不依赖 requirements.txt
RUN pip install --no-cache-dir flask

# 声明你的程序端口是 5000
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]
