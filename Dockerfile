# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY merge_videos.py /app/

# 安装必要的包
RUN pip install --no-cache-dir argparse

# 安装cron
RUN apt-get update && \
    apt-get install -y ffmpeg cron bash bash-completion && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 配置 bash-completion
RUN echo "source /etc/profile" >> ~/.bashrc

# 创建cron任务文件
RUN echo "0 * * * * python /app/merge_videos.py" >> /etc/cron.d/merge_videos

# 给cron任务文件添加可执行权限
RUN chmod 0644 /etc/cron.d/merge_videos

# 应用 cron 任务
RUN crontab /etc/cron.d/merge_videos

# 启动cron服务
CMD ["cron", "-f"]
