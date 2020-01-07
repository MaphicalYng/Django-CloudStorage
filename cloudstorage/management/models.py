from django.db import models
from user.models import User


# 文件类型表
class FileType(models.Model):
    # 选择序号
    select_id = models.IntegerField(primary_key=True)

    # 类型显示名称
    display_name = models.CharField(max_length=64, blank=False)

    # 文件扩展名
    ext_name = models.CharField(max_length=32, blank=False)

    def __str__(self):
        return self.display_name


# 文件模块数据表
# 文件表
class File(models.Model):
    # 文件的显示名称
    display_name = models.CharField(max_length=128, blank=False)

    # 文件的路径实际名称
    real_name = models.CharField(max_length=32, blank=False)

    # 文件所处服务器路径
    current_path = models.CharField(max_length=2048, blank=False)

    # 文件上传时间
    upload_time = models.DateTimeField(blank=False)

    # 文件所属的用户ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    # 是否删除
    if_delete = models.BooleanField(blank=False)

    # 是否是文件夹
    if_dir = models.BooleanField(blank=False)

    # 文件类型
    file_type = models.ForeignKey(FileType, on_delete=models.DO_NOTHING, blank=True)

    # 文件大小
    file_size = models.BigIntegerField(blank=False)

    def __str__(self):
        return self.real_name


# 管理模块数据表
# 分享链接表
class ShareLink(models.Model):
    # 创建时间
    create_time = models.DateTimeField(blank=False)

    # Token
    token = models.CharField(max_length=64, blank=False)

    # 有效时间
    valid_period = models.IntegerField(blank=False)

    # 引用文件，文件删除时链接级联删除
    target_file = models.ForeignKey(File, related_name='target_file', on_delete=models.CASCADE, blank=False)

    # 所属的用户，用户删除时链接级联删除（为扩展多用户系统做准备）
    user = models.ForeignKey(User, related_name='user_belong', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.token


# 留言表
class Message(models.Model):
    # 留言者昵称
    nickname = models.CharField(max_length=64, blank=False)

    # 留言标题
    title = models.CharField(max_length=128, blank=False)

    # 留言内容
    content = models.TextField(max_length=1024, blank=False)

    # 创建时间
    create_time = models.DateTimeField(blank=False)

    # 关联的链接，链接删除时留言级联删除
    target_link = models.ForeignKey(ShareLink, related_name='target_link', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.title
