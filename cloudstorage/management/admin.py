from django.contrib import admin

from .models import FileType, File, ShareLink, Message

# Register your models here.
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(ShareLink)
admin.site.register(Message)
