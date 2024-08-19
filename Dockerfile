# 使用官方的 Python 镜像作为基础
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到容器中
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行 Python 程序
CMD ["python", "main.py"]
