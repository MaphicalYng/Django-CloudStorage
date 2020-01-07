from django.db import models


# 用户表
# Create your models here.
class User(models.Model):
    # 用户邮箱
    email = models.CharField(max_length=128, blank=False)

    # 用户名
    username = models.CharField(max_length=64, blank=False)

    # 加密的密码
    password_md5 = models.CharField(max_length=32, blank=False)

    # 注册时间
    create_time = models.DateTimeField(blank=False)

    # 用户是否被审核
    if_valid = models.BooleanField(blank=False)

    # 用户所拥有的网盘空间（整数，GB）
    space = models.IntegerField(blank=False)

    # 用户剩余空间
    remain_space = models.BigIntegerField(blank=False)

    def __str__(self):
        return self.username


# 空间申请表
class SpaceApply(models.Model):
    # 申请ID
    apply_id = models.IntegerField(primary_key=True, blank=False)

    # 申请容量
    space_gb_number = models.IntegerField(blank=False)

    # 申请理由
    reason = models.CharField(max_length=2048, blank=False)

    # 关联用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.apply_id)
