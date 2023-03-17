import django.core.exceptions
from django.shortcuts import render, HttpResponse
from brelki.models import Keychain, User, Comment
from .forms import RegistrationForm, AuthForm, CreateKeychainForm, CreateCommentForm, EditCommentForm, SearchForm, \
    EditKeychainForm
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from os import remove
from django.utils.datastructures import MultiValueDictKeyError


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
                    'str_user_img': str_user_img},
               "search_form": SearchForm()}

    if request.GET:
        search_content = SearchForm(request.GET)
        if search_content.is_valid():
            return redirect('/search?search_input=' + request.GET['search_input'])
        else:
            print('not ok')

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
    request.session['user_img'] = ''
    return redirect('/')


def keychain(request):
    keychain_id = request.GET['id']
    request.session['keychain_id'] = keychain_id

    try:
        current_user_id = request.session['user_id']
    except KeyError:
        current_user_id = 0

    try:
        Keychain.objects.get(id=keychain_id)
    except ObjectDoesNotExist:
        return HttpResponse('Брелка с таким id не существует', status=404)

    context = {"keychain": Keychain.objects.get(id=keychain_id),
               "user": User.objects.all(),
               "comments": Comment.objects.order_by('-create_date').filter(keychain_id=keychain_id),
               "create_comment_form": CreateCommentForm()}

    if current_user_id != 0 and current_user_id != '':
        context['current_user'] = User.objects.get(id=current_user_id)

    # Создание комментария

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


def search(request):
    search_keychains = Keychain.objects.filter(title__contains=request.GET['search_input'])
    search_users = User.objects.filter(login__contains=request.GET['search_input'])
    return HttpResponse(render(request, 'search.html', {'search_keychains': search_keychains,
                                                        'search_users': search_users,
                                                        'search_title': request.GET['search_input']}))


def user_info(request):
    context = {"logged_user_id": int(request.session['user_id']),
               "personal_space_user_id": int(request.GET['user_id']),
               "user": User.objects.get(id=int(request.GET['user_id'])),
               "keychains": Keychain.objects.all()
               }

    try:
        user_keychains = Keychain.objects.filter(user_id=request.GET['user_id'])
        user_comments = Comment.objects.filter(user_id=request.GET['user_id'])
    except ObjectDoesNotExist:
        user_keychains = {}
        user_comments = {}

    context['user_keychains'] = user_keychains
    context['user_comments'] = user_comments

    return HttpResponse(render(request, 'user_info.html', context))


def edit_keychain(request):
    edited_keychain = Keychain.objects.get(id=request.GET['keychain_id'])
    current_keychain_image = edited_keychain.img
    if request.method == 'POST':
        form_content = EditKeychainForm(request.POST, request.FILES, instance=edited_keychain)
        if form_content.is_valid():
            edited_keychain.title = request.POST['title']
            edited_keychain.description = request.POST['description']
            edited_keychain.price = request.POST['price']
            try:
                uploaded_image = request.FILES['img']
                remove(current_keychain_image.path)
                edited_keychain.img = uploaded_image
            except MultiValueDictKeyError:
                pass

            edited_keychain.save()
            return redirect('/')
        else:
            return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': form_content}))
    else:
        edit_keychain_form = EditKeychainForm(instance=edited_keychain)
        return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': edit_keychain_form}))
