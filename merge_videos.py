import os
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime, date

# 全局变量用于检测任务是否正在运行
LOCK_FILE = '/app/merge_videos.lock'


def get_date_from_filename(filename):
    # 从文件名中提取日期
    timestamp_str = filename.split('_')[0]
    date_str = timestamp_str[:8]
    return datetime.strptime(date_str, '%Y%m%d').date()


def check_lock_file():
    # 检查锁文件是否存在，存在则说明有任务在运行
    return os.path.exists(LOCK_FILE)


def create_lock_file():
    # 创建锁文件
    with open(LOCK_FILE, 'w') as f:
        f.write('locked')


def remove_lock_file():
    # 删除锁文件
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def merge_videos_by_day(input_dir, archive_dir, output_dir):
    # 打印环境变量
    print(f"Input directory: {input_dir}")
    print(f"Archive directory: {archive_dir}")
    print(f"Output directory: {output_dir}")

    # 检查锁文件，如果存在则退出，避免并发执行
    if check_lock_file():
        print("Another merge task is already running. Exiting.")
        return

    # 创建锁文件，表示任务开始运行
    create_lock_file()

    try:
        # 创建目标目录
        os.makedirs(archive_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 获取所有视频文件
        video_files = [f for f in os.listdir(input_dir) if f.endswith('.mp4')]

        # 根据日期分组
        videos_by_date = defaultdict(list)
        for video in video_files:
            video_date = get_date_from_filename(video)
            videos_by_date[video_date].append(video)

        # 获取今天的日期
        today = date.today()

        # 合并视频
        for video_date, videos in videos_by_date.items():
            if video_date == today:
                continue  # 跳过今天的文件

            if videos:
                print(f"Start merging videos for {video_date}...")

                # 创建文件列表内容
                file_list_content = '\n'.join([f"file '{os.path.join(input_dir, video)}'" for video in sorted(videos)])

                output_file = os.path.join(output_dir, f'{video_date}.mp4')

                # 使用命名管道（FIFO）
                fifo_path = os.path.join(input_dir, 'temp_fifo')
                os.mkfifo(fifo_path)

                # 启动 ffmpeg 进程
                process = subprocess.Popen([
                    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', fifo_path, '-c', 'copy', '-loglevel', 'error',
                    output_file
                ])

                # 将文件列表内容写入命名管道
                with open(fifo_path, 'w') as fifo:
                    fifo.write(file_list_content)

                # 等待 ffmpeg 进程完成
                process.communicate()

                # 删除命名管道
                os.remove(fifo_path)

                if process.returncode == 0:
                    # 创建日期子目录
                    date_dir = os.path.join(archive_dir, video_date.strftime('%Y%m%d'))
                    os.makedirs(date_dir, exist_ok=True)

                    # 移动原始文件到存档目录的子目录
                    for video in videos:
                        shutil.move(os.path.join(input_dir, video), os.path.join(date_dir, video))

                    print(f"Finished merging videos for {video_date}. Output saved to {output_file}")
                else:
                    print(f"Failed to merge videos for {video_date}")

    finally:
        # 删除锁文件，任务结束
        remove_lock_file()


if __name__ == "__main__":
    # 从环境变量获取参数
    input_dir = os.getenv('INPUT_DIR', '/data/xiaomi_camera_video/')
    archive_dir = os.getenv('ARCHIVE_DIR', '/data/xiaomi_camera_merged/')
    output_dir = os.getenv('OUTPUT_DIR', '/data/xiaomi_camera_video_output/')

    merge_videos_by_day(input_dir, archive_dir, output_dir)
