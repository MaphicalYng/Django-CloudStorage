import hashlib
import json
import os
from datetime import datetime
from django.shortcuts import render, redirect
from management.file.tool import StorageDirectory
from management.tool import HasNoPermissionError, MessageController
from django.http import HttpResponse, FileResponse
from management.tool import HasNoRemainFullSpaceError
from user.tool import RoleUser, UserSpaceController, UserHasNotBeenPermittedError
from management.tool import AuthController
from management.tool import FileController


# Create your views here.
def show_file_list_page(request, path):
    """
    显示目录文件列表页面。
    :param path: 要查看的目录路径
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if path == '-/':
            # 根目录
            d = StorageDirectory(current_path='', real_name='', username=user.get_username())
            path = ''
            if_root = True
            # 用于回退网页
            last_path = None
        else:
            # 其他目录
            path_list_temp = path.split('/')
            path_list = []
            for p in path_list_temp:
                if p != '':
                    path_list.append(p)
            real_name = path_list[-1]
            if len(path_list) > 1:
                real_path = os.path.sep.join(path_list[0:-1])
                last_path = '/'.join(path_list[0:-1])
            else:
                real_path = ''
                last_path = '-'
            d = StorageDirectory(current_path=real_path, real_name=real_name, username=user.get_username())
            if_root = False
            print('path_list: ', path_list, 'real_path: ', real_path, 'last_path: ', last_path)
        dir_list, file_list = d.get_inner_objects()
        context = {
            'back_url': request.get_full_path(),
            'if_root': if_root,
            'last_path': last_path,
            'current_path': path,
            'dir': [],
            'file': []
        }
        i = 0
        for di in dir_list:
            if path == '':
                di_path = di.real_name
            else:
                di_path = path + di.real_name
            context['dir'].append([di.database_name, di.real_name, di.create_time, i, di_path])
            i = i + 1
        for fi in file_list:
            context['file'].append([fi.database_name, fi.real_name, fi.create_time, fi.size, i, fi.file_type])
            i = i + 1
        # 获取服务器状态
        context['username'] = user.get_username()
        status_controller = UserSpaceController(user.get_username())
        context['total_space'] = status_controller.get_user_space()
        context['remain_space'] = status_controller.get_user_remain_space_in_gb()
        context['space_rate'] = round(100 - (float(context['remain_space']) / float(context['total_space']) * 100))
        context['time'] = datetime.now()
        # 获取文件类型数据
        context['file_type'] = FileController.get_all_file_type()
        if 'if_copy' not in request.session:
            if_copy = False
        else:
            if_copy = request.session['if_copy']
        if 'if_move' not in request.session:
            if_move = False
        else:
            if_move = request.session['if_move']
        if if_move or if_copy:
            context['if_pofn'] = True
        else:
            context['if_pofn'] = False
        return render(request, 'management/index.html', context)
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def show_share_link_list_page(request):
    """
    显示所有的分享链接页面。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        file_controller = FileController(username=user.get_username())
        share_link_list = file_controller.get_all_share_list()
        context = {
            'back_url': request.get_full_path(),
            'link_list': []
        }
        i = 0
        for link in share_link_list:
            if link.if_valid():
                v = '有效'
            else:
                v = '失效'
            context['link_list'].append(
                {
                    'i': i,
                    'filename': link.file.database_name,
                    'create_time': link.create_time,
                    'if_valid': v,
                    'token': link.token,
                    'file_path': link.file.database_name,
                    'expired_time': link.expired_time
                }
            )
            i = i + 1
        # 获取服务器状态
        context['username'] = user.get_username()
        status_controller = UserSpaceController(user.get_username())
        context['total_space'] = status_controller.get_user_space()
        context['remain_space'] = status_controller.get_user_remain_space_in_gb()
        context['space_rate'] = round(100 - (float(context['remain_space']) / float(context['total_space']) * 100))
        context['time'] = datetime.now()
        return render(request, 'management/share.html', context)
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def show_message_list_page(request, token):
    """
    显示分享链接的留言页面。
    :param token: 链接Token
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        # 获取留言
        model_link_list = MessageController.get_all_message(token)
        context = {'message_list': model_link_list, 'username': user.get_username()}
        # 获取服务器状态
        status_controller = UserSpaceController(user.get_username())
        context['total_space'] = status_controller.get_user_space()
        context['remain_space'] = status_controller.get_user_remain_space_in_gb()
        context['space_rate'] = round(100 - (float(context['remain_space']) / float(context['total_space']) * 100))
        context['time'] = datetime.now()
        return render(request, 'management/message-list.html', context)
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def show_share_download_page(request, token):
    """
    显示分享链接文件下载页面。
    :param token: 分享链接Token
    """
    context = {
        'back_url': request.get_full_path()
    }
    link = FileController.get_share_link_using_token(token=token)
    context['valid'] = link.if_valid()
    context['link'] = link
    return render(request, 'management/share_link.html', context)


def show_trash_page(request):
    """
    显示回收站的文件。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        dirs, files = FileController.list_trash(user.get_username())
        context = {
            'back_url': request.get_full_path(),
            'files': files,
            'dirs': dirs
        }
        # 获取服务器状态
        status_controller = UserSpaceController(user.get_username())
        context['total_space'] = status_controller.get_user_space()
        context['remain_space'] = status_controller.get_user_remain_space_in_gb()
        context['space_rate'] = round(100 - (float(context['remain_space']) / float(context['total_space']) * 100))
        context['time'] = datetime.now()
        return render(request, 'management/trash.html', context)
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


# APIS
def api_share_download_file(request, token):
    """
    下载分享文件的接口。
    """
    # TODO 检测登录状态
    file_obj, file_name = FileController.get_share_file(token)
    return FileResponse(file_obj, as_attachment=True, filename=file_name)


def api_upload_file(request):
    """
    接收上传文件的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            file_name = request.POST.get('file_name', None)
            file = request.FILES.get('file', None)
            file_type_select_id = request.POST.get('file_type_select_id', None)
            back_url = request.POST.get('back_url', None)
            FileController.upload_file(
                current_path=current_path,
                byte_data=file,
                name=file_name,
                username=user.get_username(),
                file_type_select_id=file_type_select_id,
                file_size_in_kb=(file.size / 1024)
            )
            return redirect(back_url)
        return HttpResponse('方法错误。')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')
    except HasNoRemainFullSpaceError as e:
        return __return_error_page(request, e, back_url)


def api_download_file(request, real_name):
    """
    下载文件的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            file_obj, name = FileController.download_file(
                current_path=current_path, real_name=real_name, username=user.get_username())
            return FileResponse(file_obj, as_attachment=True, filename=name)
        return HttpResponse('失败！')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_delete_file(request, real_name):
    """
    删除文件的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.delete_file(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('失败！')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_rename_file(request, real_name):
    """
    重命名文件的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            new_name = request.POST.get('new_name', None)
            back_url = request.POST.get('back_url', None)
            FileController.rename_file(
                current_path=current_path, real_name=real_name, new_name=new_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('失败！')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_create_directory(request):
    """
    创建目录的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            new_name = request.POST.get('directory_name', None)
            back_url = request.POST.get('back_url', None)
            FileController.create_directory(current_path=current_path, name=new_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('失败！')
    except HasNoPermissionError as e:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_delete_directory(request, real_name):
    """
    删除目录的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.delete_directory(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('失败！')
    except HasNoPermissionError as e:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_rename_directory(request, real_name):
    """
    重命名对象的接口。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            new_name = request.POST.get('new_name', None)
            back_url = request.POST.get('back_url', None)
            FileController.rename_directory(
                current_path=current_path, real_name=real_name, new_name=new_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('失败！')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_add_message(request, token):
    """
    添加留言的接口。
    """
    if request.method == 'POST':
        nickname = request.POST.get('nickname', None)
        title = request.POST.get('title', None)
        content = request.POST.get('content', None)
        back_url = request.POST.get('back_url', None)
        MessageController.add_message(token=token, nickname=nickname, title=title, content=content)
        return __return_success_page(request, '留言成功', '您已留言成功，文件主人会看到您的留言。', back_url)
    return HttpResponse('错误方法')


def api_create_share_link(request, real_name):
    """
    创建分享链接。
    """
    if request.method == 'POST':
        current_path = request.POST.get('current_path', None)
        valid_period = int(request.POST.get('day', None))
        username = request.POST.get('username', None)
        back_url = request.POST.get('back_url', None)
        FileController.create_share_link(
            current_path=current_path, real_name=real_name, valid_period=valid_period, username=username)
        return redirect(back_url)
    return HttpResponse('创建失败！')


def api_delete_share_link(request, token):
    """
    删除分享链接。
    """
    FileController.delete_share_link(token=token)
    back_url = request.POST.get('back_url', None)
    return redirect(back_url)


def api_apply_space(request):
    """
    用户申请新的空间。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            new_space = request.POST.get('new_space', None)
            reason = request.POST.get('reason', None)
            back_url = request.POST.get('back_url', None)
            if new_space and reason:
                user_space_controller = UserSpaceController(user.get_username())
                user_space_controller.apply_new_space(number=new_space, reason=reason)
                return __return_success_page(request, '操作结果', '您的申请已提交，请等待管理员审核。', back_url)
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def __return_message_page(request, title, content, redirect_input):
    message_data = {
        'message': {
            'title': title,
            'content': content,
            'create_time': datetime.now(),
            'redirect': redirect_input,
            'type': 'primary'
        }
    }
    return render(request, 'management/message.html', message_data)


def __return_success_page(request, title, content, redirect_input, auto_redirect=True):
    message_data = {
        'message': {
            'title': title,
            'content': content,
            'create_time': datetime.now(),
            'redirect': redirect_input,
            'type': 'success',
            'auto_redirect': auto_redirect
        }
    }
    return render(request, 'management/message.html', message_data)


def __return_error_page(request, e, redirect_input):
    message_data = {
        'message': {
            'title': '错误',
            'content': e.message,
            'create_time': datetime.now(),
            'redirect': redirect_input,
            'type': 'danger'
        }
    }
    return render(request, 'management/message.html', message_data)


def api_set_copy(request):
    """
    标记需要复制的文件。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        json_data = json.loads(request.body)
        dir_real_name_list = json_data['dir_real_name_list']
        file_real_name_list = json_data['file_real_name_list']
        current_path = json_data['current_path']
        request.session['copy_real_name_list_dir'] = dir_real_name_list
        request.session['copy_real_name_list_file'] = file_real_name_list
        request.session['copy_file_current_path'] = current_path
        request.session['if_copy'] = True
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_do_copy(request):
    """
    执行复制操作。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        json_data = json.loads(request.body)
        current_path = json_data['current_path']
        copy_current_path = request.session['copy_file_current_path']
        copy_dir_real_name_list = request.session['copy_real_name_list_dir']
        copy_file_real_name_list = request.session['copy_real_name_list_file']
        request.session['if_copy'] = False
        if current_path != '-/':
            target_real_name = current_path.split('/')
            temp_array = []
            for item in target_real_name:
                if item != '':
                    temp_array.append(item)
            target_real_name = '/'.join(temp_array)
            target_real_name = target_real_name.split('/')[-1]
        else:
            target_real_name = ''
        for copy_file_real_name in copy_file_real_name_list:
            FileController.copy_file(
                current_path=copy_current_path,
                real_name=copy_file_real_name,
                target_real_name=target_real_name,
                username=user.get_username()
            )
        for copy_dir_real_name in copy_dir_real_name_list:
            FileController.copy_directory(
                current_path=copy_current_path,
                real_name=copy_dir_real_name,
                target_real_name=target_real_name,
                username=user.get_username()
            )
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_set_move(request):
    """
    标记文件移动。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        json_data = json.loads(request.body)
        dir_real_name_list = json_data['dir_real_name_list']
        file_real_name_list = json_data['file_real_name_list']
        current_path = json_data['current_path']
        request.session['move_real_name_list_dir'] = dir_real_name_list
        request.session['move_real_name_list_file'] = file_real_name_list
        request.session['move_file_current_path'] = current_path
        request.session['if_move'] = True
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_do_move(request):
    """
    进行移动操作。
    """
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        json_data = json.loads(request.body)
        current_path = json_data['current_path']
        move_current_path = request.session['move_file_current_path']
        move_dir_real_name_list = request.session['move_real_name_list_dir']
        move_file_real_name_list = request.session['move_real_name_list_file']
        request.session['if_move'] = False
        if current_path != '-/':
            target_real_name = current_path.split('/')
            temp_array = []
            for item in target_real_name:
                if item != '':
                    temp_array.append(item)
            target_real_name = '/'.join(temp_array)
            target_real_name = target_real_name.split('/')[-1]
        else:
            target_real_name = ''
        for move_file_real_name in move_file_real_name_list:
            FileController.move_file(
                current_path=move_current_path,
                real_name=move_file_real_name,
                target_real_name=target_real_name,
                username=user.get_username()
            )
        for move_dir_real_name in move_dir_real_name_list:
            FileController.move_directory(
                current_path=move_current_path,
                real_name=move_dir_real_name,
                target_real_name=target_real_name,
                username=user.get_username()
            )
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_recycle_file(request, real_name):
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.recycle_file(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_recycle_directory(request, real_name):
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.recycle_directory(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_recover_file(request, real_name):
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.recover_file(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')


def api_recover_directory(request, real_name):
    try:
        user = RoleUser(request.session)
        auth = AuthController(user)
        auth.do_auth()
        if request.method == 'POST':
            current_path = request.POST.get('current_path', None)
            back_url = request.POST.get('back_url', None)
            FileController.recover_directory(current_path=current_path, real_name=real_name, username=user.get_username())
            return redirect(back_url)
        return HttpResponse('OK')
    except HasNoPermissionError:
        # 未登录
        return redirect('/user/login/')
    except UserHasNotBeenPermittedError as e:
        user.logout()
        return __return_error_page(request, e, '/user/login/')
