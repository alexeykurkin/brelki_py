from django.shortcuts import render, HttpResponse
from brelki.models import Keychain, User, Comment
from .forms import RegistrationForm, AuthForm, CreateKeychainForm, CreateCommentForm, EditCommentForm
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages


def index(request):
    try:
        user_login = request.session['user_login']
        user_id = request.session['user_id']
        str_user_img = request.session['str_user_img']
    except KeyError:
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
                messages.add_message(request, messages.INFO, '???????????????? ?????????? ?????? ????????????')
                return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))

            if check_user:
                if check_password(request.POST['password'], check_user.password):
                    request.session['user_login'] = request.POST['login']
                    request.session['user_id'] = check_user.id
                    request.session['str_user_img'] = str(check_user.user_img)
                    return redirect('/')
                else:
                    messages.add_message(request, messages.INFO, '???????????????? ?????????? ?????? ????????????')
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
    request.session['user_img'] = ''
    return redirect('/')


def keychain(request):
    keychain_id = request.GET['id']
    request.session['keychain_id'] = keychain_id

    try:
        current_user_id = request.session['user_id']
    except KeyError:
        current_user_id = 0

    context = {"keychain": Keychain.objects.get(id=keychain_id),
               "user": User.objects.all(),
               "comments": Comment.objects.filter(keychain_id=keychain_id),
               "current_user": User.objects.get(id=current_user_id),
               "create_comment_form": CreateCommentForm()}

    # ???????????????? ??????????????????????

    if request.method == 'POST':
        form_content = CreateCommentForm(request.POST)
        if form_content.is_valid():

            new_comment = Comment(
                content=request.POST['content'],
                user_id=current_user_id,
                keychain_id=keychain_id
            )
            new_comment.save()

        else:
            context["create_comment_form"] = form_content
            return HttpResponse(render(request, 'keychain.html', context))
    else:
        context['create_comment_form'] = CreateCommentForm(None)
        return HttpResponse(render(request, 'keychain.html', context))

    return HttpResponse(render(request, 'keychain.html', context))


def create_keychain(request):
    if request.method == 'POST':
        form_content = CreateKeychainForm(request.POST, request.FILES)
        if form_content.is_valid():
            new_keychain = Keychain(
                title=request.POST['title'],
                description=request.POST['description'],
                user_id=request.session['user_id'],
                img=request.FILES['img'],
                price=request.POST['price']
            )
            new_keychain.save()
            return redirect('/')
        else:
            return HttpResponse(render(request, 'create_keychain.html', {'create_keychain_form': form_content}))
    else:
        create_keychain_form = CreateKeychainForm(None)
        return HttpResponse(render(request, 'create_keychain.html', {'create_keychain_form': create_keychain_form}))


def delete_comment(request):
    Comment.objects.filter(id=request.GET['comment_id']).delete()
    return redirect('/keychain?id=' + request.session['keychain_id'])


def edit_comment(request):
    current_user = User.objects.get(id=request.session['user_id'])
    comment = Comment.objects.get(id=request.GET['comment_id'])
    if request.method == 'POST':

        form_content = EditCommentForm(request.POST, initial={'content': comment.content})
        if form_content.is_valid():
            edited_comment = Comment.objects.get(id=request.GET['comment_id'])
            edited_comment.content = request.POST['content']
            edited_comment.save()
            return redirect('/keychain?id=' + request.session['keychain_id'])
        else:
            return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": form_content,
                                                                      "current_user": current_user}))
    else:
        edit_comment_form = EditCommentForm(initial={'content': comment.content})
        return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": edit_comment_form,
                                                                  "current_user": current_user}))

