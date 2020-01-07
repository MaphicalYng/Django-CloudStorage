from datetime import datetime

from django.shortcuts import render, redirect
from user.tool import RoleUser, Role, UserModuleBaseException


# Create your views here.
def show_login_page(request):
    """
    显示登录页面。
    """
    # 判断是否登录
    user = Role(request.session)
    if user.if_login():
        return redirect('/manage/list/-/')
    return render(request, 'user/login.html')


# APIS
def api_login(request):
    """
    登录的接口。
    """
    try:
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            if username and password:
                user = RoleUser(request.session, username)
                user.login(password)
    except UserModuleBaseException as e:
        context = {
            'message': {
                'title': '登录失败',
                'content': e.message,
                'create_time': datetime.now(),
                'redirect': '/user/login/',
                'type': 'danger'
            }
        }
        return render(request, 'user/message.html', context)
    return redirect('/manage/list/-/')


def api_logout(request):
    """
    登出的接口。
    """
    user = RoleUser(request.session)
    user.logout()
    context = {'message': {
        'title': '登出成功',
        'content': '您已登出，即将跳转到登录页面。',
        'create_time': datetime.now(),
        'redirect': '/user/login/',
        'type': 'success'
    }}
    return render(request, 'management/message.html', context)


def api_register(request):
    """
    用户注册。
    """
    try:
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            email = request.POST.get('email', None)
            if username and password and email:
                user = RoleUser(request.session, username=username)
                user.register(new_password=password, email=email)
                context = {
                    'message': {
                        'title': '注册成功',
                        'content': '注册成功，请等待管理员审核。',
                        'create_time': datetime.now(),
                        'redirect': '/user/login/',
                        'type': 'success'
                    }
                }
                return render(request, 'user/message.html', context)
    except UserModuleBaseException as e:
        context = {
            'message': {
                'title': '注册失败',
                'content': e.message,
                'create_time': datetime.now(),
                'redirect': '/user/login/',
                'type': 'danger'
            }
        }
        return render(request, 'user/message.html', context)
    return redirect('/manage/list/-/')
