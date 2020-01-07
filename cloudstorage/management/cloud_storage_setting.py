import os
import hashlib
"""
此文件是云盘的配置文件。
"""


class CloudStorageSetting(object):
    """
    配置类的定义，修改以配置。
    """
    # 云盘存储目录的位置
    STORAGE_PATH = "E:\\cloud_storage"

    # 工作临时目录
    TEMP_PATH = "E:\\cloud_storage_temp"

    def __init__(self, username=None):
        if username:
            md5 = hashlib.md5(username.encode('utf-8')).hexdigest()
            self.STORAGE_PATH = os.path.join(self.STORAGE_PATH, md5)
            # 检查目录是否存在
            if not os.path.exists(self.STORAGE_PATH):
                # 创建目录
                os.mkdir(self.STORAGE_PATH)
            if not os.path.exists(self.TEMP_PATH):
                # 创建目录
                os.mkdir(self.TEMP_PATH)
