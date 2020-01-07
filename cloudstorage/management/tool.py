import os
import psutil
import random
from datetime import datetime
import datetime as dt
from user.models import User as ModelUser
from management.models import File as ModelFile
from management.models import ShareLink as ModelShareLink
from management.models import Message as ModelMessage
from management.models import FileType as ModelFileType
from management.file.tool import StorageFile, StorageDirectory, DataBackupController
from management.cloud_storage_setting import CloudStorageSetting
from user.tool import UserSpaceController

"""
此文件是管理模块工具类代码文件，包含各种控制器的实现。
"""


class StatusController(object):
    """
    读取服务器状态的工具类。
    """
    # 磁盘总空间GB
    storage_total_space = None

    # 磁盘剩余空间GB
    storage_remain_space = None

    # 构造方法，为属性赋值
    def __init__(self):
        usage = psutil.disk_usage(CloudStorageSetting().STORAGE_PATH)
        self.storage_total_space = format(usage[0] / 1024 / 1024 / 1024, '.2f')
        self.storage_remain_space = format(usage[2] / 1024 / 1024 / 1024, '.2f')


class ShowController(object):
    """
    读取服务器文件并返回存储对象列表的工具类。
    """
    # 当前路径存储对象列表
    current_path_directory_list = None
    current_path_file_list = None

    # 为属性赋值
    def __init__(self, current_path, username):
        # 使用文件模块读取当前路径列表
        # 将URL正斜杠转换为操作系统的文件分割符
        current_path = os.path.sep.join(current_path.split('/'))
        d = StorageDirectory(current_path=current_path, real_name='', username=username)
        self.current_path_directory_list, self.current_path_file_list = d.get_inner_objects()


class FileController(object):
    """
    操控文件模块的工具类。
    """

    # 为成员变量赋值
    def __init__(self, username):
        self.username = username

    # 获取此用户所有的分享链接
    def get_all_share_list(self):
        # 读取所有的分享链接
        model_list = ModelShareLink.objects.filter(user__username=self.username)
        all_share_link_list = []
        for model in model_list:
            all_share_link_list.append(
                ShareLink(
                    model.token,
                    StorageFile(
                        current_path=model.target_file.current_path,
                        real_name=model.target_file.real_name,
                        username=model.user.username
                    ),
                    create_time=model.create_time,
                    valid_period=model.valid_period,
                    username=self.username
                )
            )
        return all_share_link_list

    # 根据token获取分享链接对象
    @staticmethod
    def get_share_link_using_token(token):
        # 根据token获得链接对象
        model = ModelShareLink.objects.get(token=token)
        return ShareLink(
            model.token,
            StorageFile(
                current_path=model.target_file.current_path,
                real_name=model.target_file.real_name,
                username=model.user.username
            ),
            create_time=model.create_time,
            valid_period=model.valid_period,
            username=model.user.username
        )

    # 创建分享链接，有效时间单位：天
    @staticmethod
    def create_share_link(current_path, real_name, valid_period, username):
        current_path = os.path.sep.join(current_path.split('/'))
        file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        new_link = ShareLink(None, file=file, create_time=datetime.now(), valid_period=valid_period, username=username)
        new_link.gen_new_token()
        # 存入数据库
        # 搜索目标文件
        target_file = ModelFile.objects.get(real_name=file.real_name)
        user = ModelUser.objects.get(username=username)
        model_new_link = ModelShareLink(
            create_time=datetime.now(),
            token=new_link.token,
            valid_period=valid_period,
            target_file=target_file,
            user=user
        )
        model_new_link.save()

    # 删除分享链接
    @staticmethod
    def delete_share_link(token):
        model_share_link = ModelShareLink.objects.get(token=token)
        model_share_link.delete()

    # 获得分享链接指向的文件
    @staticmethod
    def get_share_file(token):
        # 搜索分享链接
        expired_period = ModelShareLink.objects.get(token=token).valid_period
        create_time = ModelShareLink.objects.get(token=token).create_time
        # 检测是否过期
        expired_time = create_time + dt.timedelta(days=expired_period)
        if datetime.now().timestamp() > expired_time.timestamp():
            raise ShareLinkExpiredError()
        model_link_target_file = ModelShareLink.objects.get(token=token).target_file
        storage_file = StorageFile(
            current_path=model_link_target_file.current_path,
            real_name=model_link_target_file.real_name,
            username=model_link_target_file.user.username
        )
        return storage_file.get(), storage_file.database_name

    # 上传文件
    @staticmethod
    def upload_file(current_path, byte_data, file_type_select_id, file_size_in_kb, name, username):
        user_space_controller = UserSpaceController(username=username)
        if user_space_controller.if_full(file_size_in_kb):
            raise HasNoRemainFullSpaceError()
        current_path = os.path.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, database_name=name, username=username)
        storage_file.create(file_type_select_id=file_type_select_id, byte_data=byte_data, new_add_space_in_kb=file_size_in_kb)

    # 下载文件
    @staticmethod
    def download_file(current_path, real_name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        return storage_file.get(), storage_file.database_name

    # 删除文件
    @staticmethod
    def delete_file(current_path, real_name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.delete()

    # 创建目录
    @staticmethod
    def create_directory(current_path, name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, database_name=name, username=username)
        storage_directory.create()

    # 删除目录
    @staticmethod
    def delete_directory(current_path, real_name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.delete()

    # 重命名文件
    @staticmethod
    def rename_file(current_path, real_name, new_name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.rename(new_name=new_name)

    # 重命名目录
    @staticmethod
    def rename_directory(current_path, real_name, new_name, username):
        current_path = os.path.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.rename(new_name=new_name)

    # 复制文件
    @staticmethod
    def copy_file(current_path, real_name, target_real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.copy(target_dir_real_name=target_real_name)

    # 复制目录
    @staticmethod
    def copy_directory(current_path, real_name, target_real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.copy(target_dir_real_name=target_real_name)

    # 将文件放入回收站中
    @staticmethod
    def recycle_file(current_path, real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.recycle()

    # 将目录放入回收站
    @staticmethod
    def recycle_directory(current_path, real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.recycle()

    @staticmethod
    def recover_file(current_path, real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.recover()

    @staticmethod
    def recover_directory(current_path, real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.recover()

    # 将文件移动到新目录
    @staticmethod
    def move_file(current_path, real_name, target_real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_file = StorageFile(current_path=current_path, real_name=real_name, username=username)
        storage_file.copy(target_dir_real_name=target_real_name)
        storage_file.delete()

    # 将目录移动到新目录
    @staticmethod
    def move_directory(current_path, real_name, target_real_name, username):
        current_path = os.sep.join(current_path.split('/'))
        storage_directory = StorageDirectory(current_path=current_path, real_name=real_name, username=username)
        storage_directory.copy(target_dir_real_name=target_real_name)
        storage_directory.delete()

    @staticmethod
    def list_trash(username):
        files = ModelFile.objects.filter(if_delete=True, if_dir=False, user__username=username)
        dirs = ModelFile.objects.filter(if_delete=True, if_dir=True, user__username=username)
        return dirs, files

    @staticmethod
    def get_all_file_type():
        types = ModelFileType.objects.all()
        return types

    @staticmethod
    def encrypt_all_data(target_dir):
        data_controller = DataBackupController()
        data_controller.make_targz(CloudStorageSetting().STORAGE_PATH)
        return data_controller.encrypt_file(target_dir)


class ShareLink(object):
    """
    分享链接的实体类。
    """
    # 指向的文件
    file = None

    # 链接的Token
    token = None

    # 创建时间
    create_time = None

    # 过期时间
    expired_time = None

    # 链接用户
    username = None

    # 根据Token读取文件和信息
    def __init__(self, token, file, create_time, valid_period, username):
        self.token = token
        self.file = file
        self.create_time = create_time
        self.expired_time = create_time + dt.timedelta(days=valid_period)
        self.username = username

    # 为新创建的Link创建Token
    def gen_new_token(self):
        self.token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))

    # 判断目前是否有效
    def if_valid(self):
        return datetime.now().timestamp() <= self.expired_time.timestamp()


class AuthController(object):
    """
    鉴权控制器工具类。
    """
    # 当前需要鉴权的用户对象
    current_user = None

    # 为成员变量赋值
    def __init__(self, current_user):
        self.current_user = current_user

    # 进行鉴权
    def do_auth(self):
        # 通过Session进行鉴权
        if not self.current_user.if_login():
            raise HasNoPermissionError()
        self.current_user.do_permit()


class MessageController(object):
    """
    留言控制器。
    """
    # 获得所有的与链接相关的留言
    @staticmethod
    def get_all_message(token):
        target_link = ModelShareLink.objects.get(token=token)
        return ModelMessage.objects.filter(target_link=target_link)

    # 添加留言
    @staticmethod
    def add_message(token, nickname, title, content):
        target_link = ModelShareLink.objects.get(token=token)
        new_message = ModelMessage(
            nickname=nickname,
            title=title,
            content=content,
            create_time=datetime.now(),
            target_link=target_link
        )
        new_message.save()


class ManagementModuleBaseException(BaseException):
    """
    管理模块异常基类。
    """
    pass


class ShareLinkExpiredError(ManagementModuleBaseException):
    """
    分享链接过期异常类定义。
    """
    def __init__(self):
        super(ShareLinkExpiredError, self).__init__()
        self.message = '此分享链接已经过期。'


class HasNoPermissionError(ManagementModuleBaseException):
    """
    无权限异常类定义。
    """
    def __init__(self):
        super(HasNoPermissionError, self).__init__()
        self.message = '您无权执行此操作。'


class HasNoRemainFullSpaceError(ManagementModuleBaseException):
    """
    用户没有足够的空间异常类定义。
    """
    def __init__(self):
        super(HasNoRemainFullSpaceError, self).__init__()
        self.message = '您没有足够的空间上传此文件。'
