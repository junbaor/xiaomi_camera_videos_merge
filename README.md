### 小米摄像头视频文件合并

#### 目的
将小米摄像头拆分较为零散的视频文件，按天合并为一个完整的视频文件

#### 环境
* python3.6
* ffmpeg

#### 构建
```shell
# 构建 docker image
docker build -t xiaomi_camera_videos_merge  .

# 打包以便上传到极空间
docker save -o xiaomi_camera_videos_merge.tar xiaomi_camera_videos_merge

# 在其他机器上加载 tar 镜像（极空间可以从页面上直接加载）
docker load -i xiaomi_camera_videos_merge.tar
```
