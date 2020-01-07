import os
import sys
import random
from datetime import datetime
import tarfile
import rsa

from management.cloud_storage_setting import CloudStorageSetting
from management.models import File, FileType
from django.core.exceptions import ObjectDoesNotExist
from user.models import User
from user.tool import UserSpaceController

"""
此文件是文件模块工具类代码文件，
包含系统操作文件和目录的代码，以及对文件和目录名称的管理。
"""


class StorageObject(object):
    """
    存储对象类。
    """
    # 真实路径名称
    real_name = None

    # 数据库名称（显示名称）
    database_name = None

    # 当前服务器路径
    current_path = None

    # 创建时间
    create_time = None

    # 对象所属用户
    user = None

    # 为成员变量赋值
    def __init__(self, real_name, database_name, current_path, username):
        self.real_name = real_name
        self.database_name = database_name
        self.current_path = current_path
        self.user = User.objects.get(username=username)

    # 在服务器上创建新对象
    def create(self, byte_data, new_add_space_in_kb):
        pass

    # 删除此对象
    def delete(self):
        pass

    # 重命名此对象
    def rename(self, new_name):
        pass

    # 将对象放入回收站
    def recycle(self):
        pass

    # 复制对象到特定路径
    def copy(self, target_path):
        pass


class StorageFile(StorageObject):
    """
    存储文件类。
    """
    # 文件大小(KBytes)
    size = None

    # 初始化成员变量
    def __init__(self, current_path, username, real_name=None, database_name=None):
        # 确保current_path最后没有分隔符
        array = []
        for item in current_path.split(os.path.sep):
            if item != '':
                array.append(item)
        current_path = os.path.sep.join(array)
        super(StorageFile, self).__init__(
            real_name=real_name, database_name=database_name, current_path=current_path, username=username)
        # 读取文件列表，或访问下载删除时
        if self.real_name is not None:
            self.size = os.path.getsize(
                os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
            ) / 1024
            self.database_name = File.objects.get(real_name=self.real_name, if_dir=False).display_name
            self.create_time = File.objects.get(real_name=self.real_name, if_dir=False).upload_time
            self.file_type = File.objects.get(real_name=self.real_name, if_dir=False).file_type.display_name

    # 上传（创建）文件，使用数据库名称生成实际名称
    def create(self, file_type_select_id, new_add_space_in_kb, byte_data=None):
        # 生成真实名称
        while True:
            self.real_name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
            try:
                File.objects.get(real_name=self.real_name)
            except ObjectDoesNotExist:
                break
        # 创建文件
        file_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
        f = open(file_path, 'wb')
        for i in byte_data.chunks():
            f.write(i)
        f.close()
        # 注册文件到数据库
        new_file = File(
            display_name=self.database_name,
            real_name=self.real_name,
            current_path=self.current_path,
            upload_time=datetime.now(),
            user=self.user,
            if_delete=False,
            if_dir=False,
            file_type=FileType.objects.get(select_id=file_type_select_id),
            file_size=new_add_space_in_kb
        )
        new_file.save()
        # 更新文件所在目录大小数据
        directory_real_name = self.current_path.split(os.path.sep)[-1]
        if directory_real_name != '':
            # 文件不在根目录，进行目录数据修改
            target_directory = File.objects.get(real_name=directory_real_name)
            target_directory.file_size = int(target_directory.file_size) + int(new_add_space_in_kb)
            target_directory.save()
        # 更新用户空间数据
        user_space_controller = UserSpaceController(username=self.user.username)
        user_space_controller.update_remain_space(add_size_in_kb=new_add_space_in_kb, if_add=True)

    # 删除文件，使用实际名称进行删除
    def delete(self):
        file_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
        # 删除文件
        os.remove(file_path)
        # 删除数据库记录
        file_record = File.objects.get(real_name=self.real_name, if_dir=False)
        file_size = int(file_record.file_size)
        file_record.delete()
        # 更新文件所在目录的大小数据
        directory_real_name = self.current_path.split(os.path.sep)[-1]
        if directory_real_name != '':
            # 不在根目录，进行目录数据修改
            target_directory = File.objects.get(real_name=directory_real_name)
            target_directory.file_size = int(target_directory.file_size) - int(file_size)
            target_directory.save()
        # 更新用户空间数据
        user_space_controller = UserSpaceController(username=self.user.username)
        user_space_controller.update_remain_space(add_size_in_kb=file_size, if_add=False)

    # 重命名文件，使用真实名称进行重命名
    def rename(self, new_name):
        file_record = File.objects.get(real_name=self.real_name, if_dir=False)
        file_record.display_name = new_name
        file_record.save()

    # 获得此对象的File对象
    def get(self):
        file_obj = open(os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name), 'rb')
        return file_obj

    # 将文件放入回收站
    def recycle(self):
        # 将文件的if_delete字段改为Ture
        file_record = File.objects.get(real_name=self.real_name, if_dir=False)
        file_record.if_delete = True
        file_record.save()

    def recover(self):
        file_record = File.objects.get(real_name=self.real_name, if_dir=False)
        file_record.if_delete = False
        file_record.save()

    # 将文件复制到目标目录
    def copy(self, target_dir_real_name):
        # 生成真实名称
        while True:
            new_real_name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
            try:
                File.objects.get(real_name=new_real_name)
            except ObjectDoesNotExist:
                break
        if target_dir_real_name == '':
            target_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, new_real_name)
            file_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
            target_current_path = CloudStorageSetting(self.user.username).STORAGE_PATH
        else:
            # 获得目标目录对象
            target_directory = File.objects.get(real_name=target_dir_real_name, if_dir=True)
            file_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
            target_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, target_directory.current_path, target_dir_real_name, new_real_name)
            target_current_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, target_directory.current_path, target_dir_real_name)
        # 判断系统平台，据此生成复制命令
        if sys.platform == "win32":
            # Windows系统
            command = r'echo F | xcopy ' + file_path + " " + target_path
        else:
            # 类Unix系统
            command = r'cp ' + file_path + " " + target_path
        # 执行命令
        os.system(command)
        # 获取旧的文件信息
        file_old_record = File.objects.get(real_name=self.real_name, if_dir=False)
        # 拷贝文件信息
        file_new_record = File(
            display_name=file_old_record.display_name,
            real_name=new_real_name,
            current_path=target_current_path,
            upload_time=file_old_record.upload_time,
            user=file_old_record.user,
            if_delete=file_old_record.if_delete,
            if_dir=file_old_record.if_dir,
            file_type=file_old_record.file_type,
            file_size=file_old_record.file_size
        )
        file_new_record.save()
        if target_dir_real_name != '':
            # 更新目标目录的空间数据
            target_directory.file_size = int(target_directory.file_size) + int(file_old_record.file_size)
            target_directory.save()
        # 更新用户空间数据
        user_space_controller = UserSpaceController(username=self.user.username)
        user_space_controller.update_remain_space(add_size_in_kb=file_old_record.file_size, if_add=True)


class StorageDirectory(StorageObject):
    """
    存储目录类。
    """
    # 初始化成员变量
    def __init__(self, current_path, username, real_name=None, database_name=None):
        # 确保current_path最后没有分隔符
        array = []
        for item in current_path.split(os.path.sep):
            if item != '':
                array.append(item)
        current_path = os.path.sep.join(array)
        super(StorageDirectory, self).__init__(
            real_name=real_name, database_name=database_name, current_path=current_path, username=username)
        # 读取目录列表时
        if self.real_name is not None and self.real_name != '':
            self.database_name = File.objects.get(real_name=self.real_name, if_dir=True).display_name
            self.create_time = File.objects.get(real_name=self.real_name, if_dir=True).upload_time

    # 获得此目录中的所有对象，使用真实名称
    def get_inner_objects(self):
        dir_list = []
        file_list = []
        dir_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
        for file in os.listdir(dir_path):
            # 判断对象是否在回收站中，如果在就跳过
            file_temp = File.objects.get(real_name=file)
            if file_temp.if_delete:
                continue
            # 对象是目录
            if os.path.isdir(os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name, file)):
                dir_list.append(
                    StorageDirectory(
                        current_path=os.path.join(self.current_path, self.real_name),
                        real_name=file,
                        username=self.user.username
                    )
                )
            # 对象是文件
            if os.path.isfile(os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name, file)):
                file_list.append(
                    StorageFile(
                        current_path=os.path.join(self.current_path, self.real_name),
                        real_name=file,
                        username=self.user.username
                    )
                )
        return dir_list, file_list

    # 创建目录，使用数据库名称
    def create(self, byte_data=None, new_add_space_in_kb=0):
        # 生成真实名称
        while True:
            self.real_name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
            try:
                File.objects.get(real_name=self.real_name)
            except ObjectDoesNotExist:
                break
        os.mkdir(os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name))
        # 注册目录
        new_dir = File(
            display_name=self.database_name,
            real_name=self.real_name,
            upload_time=datetime.now(),
            current_path=self.current_path,
            user=self.user,
            if_delete=False,
            if_dir=True,
            file_type=FileType.objects.get(select_id=-1),
            file_size=new_add_space_in_kb
        )
        new_dir.save()
        # 此处不需要更新用户空间数据，因为目录大小为零
        pass

    # 删除目录，使用真实名称
    def delete(self):
        dir_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
        try:
            # 删除目录
            os.rmdir(dir_path)
        except OSError:
            raise DeleteNonemptyDirectoryError()
        # 删除数据库记录
        dir_record = File.objects.get(real_name=self.real_name, if_dir=True)
        dir_record.delete()
        # 此处不需要更新用户空间数据，因为删除空目录不会影响空间大小（只有空目录才被允许删除）
        pass

    # 重命名，使用真实名称
    def rename(self, new_name):
        dir_record = File.objects.get(real_name=self.real_name, if_dir=True)
        dir_record.display_name = new_name
        dir_record.save()

    # 将目录放入回收站
    def recycle(self):
        # 将目录的if_delete字段改为Ture
        file_record = File.objects.get(real_name=self.real_name, if_dir=True)
        file_record.if_delete = True
        file_record.save()

    def recover(self):
        # 将目录的if_delete字段改为Ture
        file_record = File.objects.get(real_name=self.real_name, if_dir=True)
        file_record.if_delete = False
        file_record.save()

    # 将目录复制到新的位置
    def copy(self, target_dir_real_name):
        # 生成真实名称
        while True:
            new_real_name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
            try:
                File.objects.get(real_name=new_real_name)
            except ObjectDoesNotExist:
                break
        # 获得目标目录对象
        target_directory = File.objects.get(real_name=target_dir_real_name, if_dir=True)
        file_path = os.path.join(CloudStorageSetting(self.user.username).STORAGE_PATH, self.current_path, self.real_name)
        target_path = os.path.join(
            CloudStorageSetting(self.user.username).STORAGE_PATH, target_directory.current_path, target_dir_real_name)
        # 判断系统平台，据此生成复制命令
        if sys.platform == "win32":
            # Windows系统
            command = r'echo D | xcopy /E' + file_path + " " + os.sep.join(target_path, new_real_name)
        else:
            # 类Unix系统
            command = r'cp -r ' + file_path + " " + os.path.join(target_path, new_real_name)
        # 执行命令
        os.system(command)
        # 获取旧的文件信息
        file_old_record = File.objects.get(real_name=self.real_name, if_dir=False)
        # 拷贝文件信息
        file_new_record = File(
            display_name=file_old_record.display_name,
            real_name=new_real_name,
            current_path=target_path,
            upload_time=file_old_record.upload_time,
            user=file_old_record.user,
            if_delete=file_old_record.if_delete,
            if_dir=file_old_record.if_dir,
            file_type=file_old_record.file_type,
            file_size=file_old_record.file_size
        )
        file_new_record.save()
        # 更新目标目录的大小数据
        target_directory.file_size = int(target_directory.file_size) + int(file_old_record.file_size)
        target_directory.save()
        # 修改用户空间数据
        user_space_controller = UserSpaceController(username=self.user.username)
        user_space_controller.update_remain_space(add_size_in_kb=file_old_record.file_size, if_add=True)


class DataBackupController(object):
    """
    数据备份控制器类。
    """
    temp_tar = None

    # 一次性打包整个根目录。空子目录会被打包。
    def make_targz(self, source_dir):
        self.temp_tar = os.path.join(CloudStorageSetting().TEMP_PATH, 'temp.tar.gz')
        with tarfile.open(self.temp_tar, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    # 加密文件并返回密钥
    def encrypt_file(self, target_dir):
        pubkey, privkey = rsa.newkeys(1024)
        pub = pubkey.save_pkcs1()
        pri = privkey.save_pkcs1()
        public_file_path = os.path.join(CloudStorageSetting().TEMP_PATH, 'data_backup_public_key.pem')
        private_file_path = os.path.join(CloudStorageSetting().TEMP_PATH, 'data_backup_private_key.pem')
        with open(public_file_path, 'wb+') as f:
            f.write(pub)
        with open(private_file_path, 'wb+') as f:
            f.write(pri)
        target_save_path = os.path.join(target_dir, 'data_backup.tar.gz.rsa')

        tar_file = open(self.temp_tar, 'rb')
        target_file = open(target_save_path, 'wb')
        target_data = tar_file.read(100)
        while target_data:
            data_encrypted = rsa.encrypt(target_data, pubkey)
            target_file.write(data_encrypted)
            target_data = tar_file.read(100)
        tar_file.close()
        target_file.close()

        # 删除原有文件
        os.remove(self.temp_tar)
        return public_file_path, private_file_path, target_save_path


class DeleteNonemptyDirectoryError(BaseException):
    """
    删除非空目录的异常类定义。
    """
    def __init__(self):
        self.message = '不允许删除非空目录。'
