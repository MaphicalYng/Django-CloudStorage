from django.db import models

# Create your models here.
# 管理员表
class Admin(models.Model):
    # 管理员用户名
    username = models.CharField(max_length=128, blank=False)

    # 管理员用户密码MD5
    password_md5 = models.CharField(max_length=32, blank=False)