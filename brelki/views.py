from django.shortcuts import render, HttpResponse
from brelki.models import Keychain, User
from .forms import RegistrationForm, AuthForm
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages


def index(request):
    if request.session['user_login'] and request.session['user_id']:
        user_login = request.session['user_login']
        user_id = request.session['user_id']
        str_user_img = request.session['str_user_img']
    else:
        user_login = ''
        user_id = ''
        str_user_img = ''

    context = {'keychains': Keychain.objects.all(),
               'users': User.objects.all(),
               'logged_user':
                   {'user_login': user_login,
                    'user_id': user_id,
                    'str_user_img': str_user_img}}
    return HttpResponse(render(request, 'index.html', context))


def registration(request):
    if request.method == 'POST':
        form_content = RegistrationForm(request.POST, request.FILES)
        if form_content.is_valid():
            user = User(
                login=request.POST['login'],
                email=request.POST['email'],
                password=make_password(request.POST['password']),
                telephone_number=request.POST['telephone_number'],
                user_img=request.FILES['user_img']
            )
            user.save()
            return redirect('/')
        else:
            return HttpResponse(render(request, 'registration.html', {'reg_form': form_content}))
    else:
        reg_form = RegistrationForm(None)
        return HttpResponse(render(request, 'registration.html', {'reg_form': reg_form}))


def auth(request):
    if request.method == 'POST':
        form_content = AuthForm(request.POST)
        if form_content.is_valid():

            try:
                check_user = User.objects.get(login=request.POST['login'])
            except:
                messages.add_message(request, messages.INFO, 'Неверный логин или пароль')
                return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))

            if check_user:
                if check_password(request.POST['password'], check_user.password):
                    request.session['user_login'] = request.POST['login']
                    request.session['user_id'] = check_user.id
                    request.session['str_user_img'] = str(check_user.user_img)
                    return redirect('/')
                else:
                    messages.add_message(request, messages.INFO, 'Неверный логин или пароль')
                    return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))

            else:
                return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))

        else:
            return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))
    else:
        auth_form = AuthForm(None)
        return HttpResponse(render(request, 'login.html', {'auth_form': auth_form}))


def logout(request):
    request.session['user_login'] = ''
    request.session['user_id'] = ''
    return redirect('/')
