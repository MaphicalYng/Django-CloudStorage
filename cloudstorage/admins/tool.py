import hashlib
from admins.models import Admin
from user.tool import Role,UserNotExistsError,UserPasswordInvalidError
from django.core.exceptions import ObjectDoesNotExist
"""
此文件是管理员模块的工具类代码文件，包含用户实体类和一些异常的定义。
"""

class RoleAdmin(Role):
    '''
    管理员实体类
    '''
    def login(self, input_password):
        print('input_password:' + input_password)
        password_md5 = hashlib.md5(input_password.encode('utf-8')).hexdigest()
        print('password_md5:' + password_md5)
        try:
            user_password_md5 = Admin.objects.get(username=self.username).password_md5
            print('password_md5:' + password_md5)
        except ObjectDoesNotExist:
            raise UserNotExistsError()
        if password_md5 == user_password_md5:
            self.session['if_login_admins'] = True
            self.session['adminsname'] = self.username
            return True
        else:
            raise UserPasswordInvalidError()

    # 登出此用户
    def logout(self):
        if 'if_login_admins' in self.session:
            self.session['if_login_admins'] = False

    # 判断是否登录
    def if_login(self):
        if 'if_login_admins' in self.session:
            return self.session['if_login_admins']
        else:
            return False



