# 用一个通用的基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 把当前文件夹里的所有文件复制到镜像里
COPY . .

# 声明你的程序端口是 5000
EXPOSE 5000

# 启动命令（这里用示例程序，后面教你换成你自己的）
CMD ["python", "app.py"]
