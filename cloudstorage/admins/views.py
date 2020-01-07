import hashlib

from django.shortcuts import render, redirect
from admins.tool import RoleAdmin, UserPasswordInvalidError, UserNotExistsError
from django.http import HttpResponse
from user.models import User, SpaceApply
from management.models import File, FileType
from management.tool import StatusController
from management.cloud_storage_setting import CloudStorageSetting
import os
from management.tool import FileController
from management.views import __return_success_page

from user.tool import UserSpaceController

# Create your views here.


# 主界面
# TODO 文件类型，try...catch
def show_index_page_admins(request):
    '''
    主界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['user_count'] =  User.objects.count()
        data['file_count'] =  File.objects.count()
        data['capacity'] = format(float(StatusController().storage_total_space), '.2f')
        data['users'] = User.objects.all()[0:3]
        data['noused_capacity'] = format(float(StatusController().storage_total_space)-float(StatusController().storage_remain_space), '.2f')
        data['used_capacity'] = format(float(StatusController().storage_remain_space), '.2f')
        data['nocheck_user'] = User.objects.filter(if_valid=False).count()
        img_size = 0
        for img in File.objects.filter(file_type__display_name='image'):
            img_size += img.file_size
        data['img_size'] = img_size
        music_size = 0
        for music in File.objects.filter(file_type__display_name='music'):
            music_size += music.file_size
        data['music_size'] = music_size
        video_size = 0
        for video in File.objects.filter(file_type__display_name='video'):
            video_size += video.file_size
        data['video_size'] = video_size
        word_size = 0
        for word in File.objects.filter(file_type__display_name='word'):
            word_size += word.file_size
        data['word_size'] = word_size
        return render(request,'admins/index.html',data)
    return render(request, 'admins/sign-in.html')


#用户总界面
def show_users_page_admins(request):
    '''
    用户总界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['users'] = User.objects.all()
        data['nocheck_user'] = User.objects.filter(if_valid=False).count()
        return render(request,'admins/users.html', data)
    return render(request, 'admins/sign-in.html')

#用户界面
def show_user_page_admins(request, user_id):
    '''
    用户界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        if user_id:
            data['up_user'] = User.objects.get(id=user_id)
        return render(request, 'admins/user.html', data)
    return render(request, 'admins/sign-in.html')

#审核界面
def show_check_page_admins(request):
    '''
    审核界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['nocheck_users'] = User.objects.filter(if_valid=False)
        return render(request, 'admins/check.html', data)
    return render(request, 'admins/sign-in.html')

#文件界面
def show_file_page_admins(request, file_id):
    '''
    文件界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        if file_id:
            data['up_file'] = File.objects.get(id=file_id)
            data['file_type'] = FileType.objects.all()
        return render(request, 'admins/file.html', data)
    return render(request, 'admins/sign-in.html')

#总文件界面
def show_files_page_admins(request):
    '''
    总文件界面
    :param request:
    :return:
    '''
    data ={}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['files'] = File.objects.all()
        return render(request, 'admins/files.html', data)
    return render(request, 'admins/sign-in.html')

#文件类型编辑界面
def show_change_type_page_admins(request):
    '''
    文件类型编辑界面
    :param request:
    :return:
    '''
    data={}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['file_type'] = FileType.objects.all()
        return render(request, 'admins/change_type.html', data)
    return render(request, 'admins/sign-in.html')

#数据备份并加密界面
def show_backup_page_admins(request):
    '''
    数据备份并加密界面
    :param request:
    :return:
    '''
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['dirt'] = CloudStorageSetting().STORAGE_PATH
        data['size'] = StatusController().storage_total_space
        data['rem_size'] = StatusController().storage_remain_space
        return render(request, 'admins/backup.html',data)
    return render(request, 'admins/sign-in.html')

#数据加密界面
def show_encrypt_page_admins(request):
    '''
    数据加密界面
    :param request:
    :return:
    '''
    admin = RoleAdmin(request.session)
    if admin.if_login():
        return render(request, 'admins/encrypt.html')
    return render(request, 'admins/sign-in.html')


#登陆界面
def show_sign_in_page_admins(request):
    return render(request, 'admins/sign-in.html')

#注册界面
def show_sign_up_page_admins(request):
    return render(request, 'admins/sign-up.html')

#重设密码界面
def show_reset_password_page_admins(request):
    return render(request, 'admins/reset-password.html')

def if_login_admins(request):
    '''
    检测是否登陆接口
    :param redirect:
    :return:
    '''
    admin = RoleAdmin(request.session)
    if admin.if_login():
        pass
    return render(request, 'admins/sign-in.html')


def web_page_redirect(request,redirect):
    '''
    测试前端
    :param request:
    :param redirect:
    :return:
    '''
    admin = RoleAdmin(request.session)
    if admin.if_login():
        return redirect('')
    return render(request, 'admins/'+redirect+'.html')


#申请空间页面
def show_space_check_page_admins(request):
    data = {}
    admin = RoleAdmin(request.session)
    if admin.if_login():
        data['space_apply'] = SpaceApply.objects.all()
        return render(request, 'admins/space-check.html', data)
    return render(request, 'admins/sign-in.html')


###api
# TODO url
def api_login_admins(request):
    '''
    管理员登录的接口。
    :param request:
    :return:
    '''
    try:
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            if username and password:
                admin = RoleAdmin(request.session, username)
                admin.login(password)
    except UserPasswordInvalidError as e:
        return HttpResponse(e.message)
    except UserNotExistsError as e:
        return HttpResponse(e.message)
    return redirect('/admins/index')


#TODO url
def api_logout_admins(request):
    '''
    管理员登出的接口。
    :param request:
    :return:
    '''
    user = RoleAdmin(request.session)
    user.logout()
    return redirect('/admins/sign-up')


#删除User对象
def api_del_user(request):
    User.objects.filter(id=int(request.GET.get('id'))).delete()
    return redirect('/admins/users')

#添加user对象
def api_add_user(request):
    pass

#更新user对象
def api_upd_user(request):
    print(request.POST.get('uid', False))
    if request.POST.get('uid',False):
        user = User.objects.get(id=int(request.POST.get('uid')))
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('/admins/user/'+request.POST.get('uid'))
    else:
        return redirect('/admins/user/0/')

#审核对象
def api_check_user(request):
    user = User.objects.get(id=int(request.GET.get('id')))
    user.if_valid = True
    user.save()
    return redirect('/admins/check')


#删除File对象
def api_del_file(request):
    File.objects.filter(id=int(request.GET.get('id'))).delete()
    return redirect('/admins/files')


#更新file对象
def api_upd_file(request):
    # print(request.POST.get('uid', False))
    if request.POST.get('file_id',False):
        file = File.objects.get(id=int(request.POST.get('file_id')))
        file.display_name = ''.join(request.POST.get('file_name').split('.')[:-1])+request.POST.get('ext_name')
        file.file_type = FileType.objects.get(ext_name=request.POST.get('ext_name'))
        file.save()
        return redirect('/admins/file/'+request.POST.get('file_id'))
    else:
        return redirect('/admins/file/0/')


#删除FileType对象
def api_del_file_type(request):
    FileType.objects.filter(select_id=int(request.GET.get('select_id'))).delete()
    return redirect('/admins/change_type')

#添加FileType对象
def api_add_file_type(request):
    # print(request.POST.get('type_name'))
    # print(request.POST.get('ext_name'))
    type = FileType(display_name=request.POST.get('type_name'),ext_name=request.POST.get('ext_name'))
    type.save()
    return redirect('/admins/change_type')

#备份加密处理
def api_back_up(request):
    d_name = request.POST.get('file_dirt')
    temp_array = d_name.split('/')
    temp_temp = []
    for item in temp_array:
        if item != '':
            temp_temp.append(item)
    target_dir = os.path.sep.join(temp_temp)
    public_path, private_path, save_path = FileController.encrypt_all_data(target_dir)
    return __return_success_page(
        request,
        '备份成功',
        '文件备份成功，使用tar.gz压缩后进行RSA加密，文件路径为' + save_path + '，公钥文件路径为' + public_path + '，私钥文件路径为' + private_path,
        '/admins/backup/',
        False
    )

#更新密码
def api_reset_psw(request):
    uid = int(request.POST.get('uid'))
    new_psw = request.POST.get('psw')
    psw_md5 = hashlib.md5(new_psw.encode('utf-8')).hexdigest()
    user = User.objects.get(id=uid)
    user.password_md5 = psw_md5
    user.save()
    print('/admins/user/'+request.POST.get('uid')+'/')
    return redirect('/admins/user/'+request.POST.get('uid')+'/')

#确认空间审核
def api_space_check(request):
    sid = int(request.GET.get('id'))

    apply_record = SpaceApply.objects.get(apply_id=sid)
    space_controller = UserSpaceController(apply_record.user.username)
    space_controller.permit_new_space(sid)
    return redirect("/admins/space-check/")
