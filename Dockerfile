# 用一个通用的基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，再安装依赖（这是最佳实践，能利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 把当前文件夹里的所有其他文件复制到镜像里
COPY . .

# 声明你的程序端口是 5000
EXPOSE 5000

# 启动命令（这里用示例程序，后面教你换成你自己的）
CMD ["python", "app.py"]
