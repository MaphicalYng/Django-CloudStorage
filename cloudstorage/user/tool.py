import hashlib
from datetime import datetime

from user.models import User, SpaceApply
from django.core.exceptions import ObjectDoesNotExist
"""
此文件是用户模块的工具类代码文件，包含用户实体类和一些异常的定义。
"""


class Role(object):
    """
    实体类。
    """

    # Session对象
    session = None

    # 用户名
    username = None

    # 成员变量赋值
    def __init__(self, session, username=None, type=None):
        self.session = session
        self.username = username

    # 登录此用户
    def login(self, input_password):
        pass

    # 登出此用户
    def logout(self):
        pass

    # 判断是否登录
    def if_login(self):
        pass

    # 获得用户名
    def get_username(self):
        if 'username' in self.session:
            return self.session['username']
        else:
            return None


class RoleUser(Role):
    """
    用户实体类
    """
    # 登录此用户
    def login(self, input_password):
        password_md5 = hashlib.md5(input_password.encode('utf-8')).hexdigest()
        try:
            user_password_md5 = User.objects.get(username=self.username).password_md5
        except ObjectDoesNotExist:
            raise UserNotExistsError()
        if password_md5 == user_password_md5:
            self.session['if_login'] = True
            self.session['username'] = self.username
            return True
        else:
            raise UserPasswordInvalidError()

    # 注册用户
    def register(self, new_password, email):
        # 查询是否已有相同用户名的用户
        if_exist = True
        try:
            User.objects.get(username=self.username)
        except ObjectDoesNotExist:
            if_exist = False
        if if_exist:
            raise UserHasAlreadyExistsError()
        user_record = User(
            email=email,
            username=self.username,
            password_md5=hashlib.md5(new_password.encode('utf-8')).hexdigest(),
            create_time=datetime.now(),
            if_valid=False,
            space=5,
            remain_space=5*1024*1024
        )
        user_record.save()

    # 是否被审核通过
    def do_permit(self):
        user = User.objects.get(username=self.get_username())
        if not user.if_valid:
            raise UserHasNotBeenPermittedError()

    # 登出此用户
    def logout(self):
        if 'if_login' in self.session:
            self.session['if_login'] = False

    # 判断是否登录
    def if_login(self):
        if 'if_login' in self.session:
            return self.session['if_login']
        else:
            return False


class UserSpaceController(object):
    """
    用户空间控制器
    """
    # 用户对象
    user = None

    # 初始化成员变量
    def __init__(self, username):
        self.user = User.objects.get(username=username)

    # 用户申请空间
    def apply_new_space(self, number, reason):
        new_record = SpaceApply(space_gb_number=number, reason=reason, user=self.user)
        new_record.save()

    # 用户被批准新空间
    def permit_new_space(self, apply_idx):
        apply_idx = int(apply_idx)
        target_apply_record = SpaceApply.objects.get(apply_id=apply_idx)
        used_space = int(self.user.space) * 1024 * 1024 - int(self.user.remain_space)
        self.user.space = int(target_apply_record.space_gb_number)
        self.user.remain_space = int(target_apply_record.space_gb_number) * 1024 * 1024 - used_space
        self.user.save()
        # 删除申请记录
        target_apply_record.delete()

    # 获取用户空间
    def get_user_space(self):
        return format(self.user.space, '.2f')

    def get_user_remain_space_in_gb(self):
        return format(self.user.remain_space / 1024 / 1024, '.2f')

    # 判断用户空间是否已满
    def if_full(self, add_size_in_kb):
        remain_space = int(self.user.remain_space)
        return (remain_space - int(add_size_in_kb)) < 0

    # 更新剩余空间
    def update_remain_space(self, add_size_in_kb, if_add):
        if if_add:
            self.user.remain_space = int(self.user.remain_space) - int(add_size_in_kb)
        else:
            self.user.remain_space = int(self.user.remain_space) + int(add_size_in_kb)
        self.user.save()


class UserModuleBaseException(BaseException):
    """
    用户模块的异常基类。
    """
    message = None


class UserNotExistsError(UserModuleBaseException):
    """
    用户不存在异常定义。
    """
    def __init__(self):
        super(UserNotExistsError, self).__init__()
        self.message = '用户不存在，请检查用户名拼写。'


class UserPasswordInvalidError(UserModuleBaseException):
    """
    用户密码不正确异常定义。
    """
    def __init__(self):
        super(UserPasswordInvalidError, self).__init__()
        self.message = '用户密码不正确，请检查大小写。'


class UserHasAlreadyExistsError(UserModuleBaseException):
    """
    用户注册已存在异常类。
    """
    def __init__(self):
        self.message = '此用户名已存在。'


class UserHasNotBeenPermittedError(UserModuleBaseException):
    """
    用户尚未被审核通过。
    """
    def __init__(self):
        self.message = '您的账户尚未被管理员审核通过，暂不能登录。'
