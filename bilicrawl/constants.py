# -*-coding:utf-8-*-
import os
'''下载路径是按功能分类，比如所有弹幕都在barrage目录下，
下面再生成一个视频名字的文件夹，

------barrage
      --video1
      --video2
------mp4
      --video1
      --video2

而不是按视频，
-----video1
    ---barrage
    -----mp4
-----video2
    ---barrage
    -----mp4
'''


# 下载的网址
BASE_DOWN_URL = 'http://www.jijidown.com'

# 获取当前路径
BASE_FILE_PATH = os.getcwd()

# 弹幕的下载路径
BARRAGE_BASE_DIR_NAME = os.path.join(BASE_FILE_PATH, 'barrage')

# MP3的下载路径
MP3_BASE_DIR_NAME = os.path.join(BASE_FILE_PATH, 'mp3')

# MP4的下载路径
MP4_BASE_DIR_NAME = os.path.join(BASE_FILE_PATH, 'mp4')

# FLV的下载路径
FLV_BASE_DIR_NAME = os.path.join(BASE_FILE_PATH, 'flv')

# 错误信息放置位置
ERROR_BASE_DIR_NAME = os.path.join(BASE_FILE_PATH, 'error')
