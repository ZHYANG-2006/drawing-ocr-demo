# 使用基础镜像
FROM python:3.10-buster as base

# 设置工作目录
WORKDIR /app

# 安装依赖工具和必要的库
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libaio1 \
    vim \
    unzip \
    curl \
    && apt-get clean

# 将手动下载的 Oracle Instant Client Basic Lite 版本复制到容器中
COPY instantclient-basiclite-linux.x64-19.24.0.0.0dbru.zip /tmp/

# 解压并安装 Oracle Instant Client Basic Lite 版本
RUN unzip /tmp/instantclient-basiclite-linux.x64-19.24.0.0.0dbru.zip -d /usr/local/oracle \
    && rm /tmp/instantclient-basiclite-linux.x64-19.24.0.0.0dbru.zip

# 设置 Oracle Instant Client 库的环境变量
ENV LD_LIBRARY_PATH=/usr/local/oracle/instantclient_19_24:$LD_LIBRARY_PATH

# 列出 /usr/local/oracle/ 目录中的所有文件和文件夹，检查解压路径
RUN ls -l /usr/local/oracle/

# 列出解压后的文件夹内容
RUN ls -l /usr/local/oracle/instantclient_19_8/ || ls -l /usr/local/oracle/instantclient*

# 复制项目文件
COPY . /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Django 默认端口（你要用哪个端口，可以自行调整）
EXPOSE 7007

# 默认 CMD 可以留空或者写个占位命令
CMD ["/bin/bash"]