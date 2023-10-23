from ssl import SSLSession
from django.shortcuts import render, HttpResponse
from brelki.models import Category, Keychain, User, Comment
from .forms import RegistrationForm, AuthForm, CreateKeychainForm, CreateCommentForm, EditCommentForm, SearchForm, \
    EditKeychainForm, SendEmailForm, EditUserForm
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from os import remove
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from http import cookies

def index(request):
    
    try:
        logged_user_id = request.session['logged_user_id']
        logged_user_login = User.objects.get(id=logged_user_id).login
        logged_user_img = User.objects.get(id=logged_user_id).user_img
    except:
        logged_user_login = ''
        logged_user_id = ''
        logged_user_img = ''

    try:
        filter_option = request.GET['filter']
        
        if filter_option == 'price_asc':
            keychains_list = Keychain.objects.all().order_by('price')
        elif filter_option == 'price_desc':
            keychains_list = Keychain.objects.all().order_by('-price')
                
        if 'popularity' in filter_option:
            keychains_list = Keychain.objects.all()
            keychains_popularity = request.session['user_views']
            for keychain in keychains_list:
                if str(keychain.id) in keychains_popularity:
                    keychain.popularity = len(keychains_popularity[str(keychain.id)])
                else:
                    keychain.popularity = 0
            import operator
            if filter_option == 'popularity_asc':          
                keychains_list = sorted(keychains_list, key=operator.attrgetter('popularity'))  
            else:
                keychains_list = sorted(keychains_list, key=operator.attrgetter('popularity'), reverse=True)

        if 'category' in filter_option:
            keychains_list = Keychain.objects.all().filter(category=filter_option[filter_option.find('_')+1:])
            
        if filter_option == '':
            keychains_list = Keychain.objects.all()
    except:
        filter_option = ''
        keychains_list = Keychain.objects.all()

    paginator = Paginator(keychains_list, per_page=6)
    try:
        current_page = request.GET['page']
    except KeyError:
        return redirect(f'/?page=1&filter={filter_option}')

    keychains = paginator.get_page(current_page)

    context = {'keychains': keychains,
               'categories': Category.objects.all(),
               'users': User.objects.all(),
               'filter_option': filter_option,
               'logged_user':
                   {'logged_user_login': logged_user_login,
                    'logged_user_id': logged_user_id,
                    'logged_user_img': logged_user_img},
               "search_form": SearchForm()}

    if request.GET:
        search_content = SearchForm(request.GET)
        if search_content.is_valid():
            return redirect('/search?search_input=' + request.GET['search_input'])
    HttpResponse(render(request, 'menu_header.html', context))
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
                    request.session['logged_user_id'] = check_user.id
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
    request.session['logged_user_id'] = ''
    request.session['history'] = []
    return redirect('/')


def keychain(request):
    try:
        logged_user_id = request.session['logged_user_id']
        logged_user_login = User.objects.get(id=logged_user_id).login
        logged_user_img = User.objects.get(id=logged_user_id).user_img

    except:
        logged_user_id = ''
        logged_user_login = ''
        logged_user_img = ''

    keychain_id = request.GET['id']

    try:
        request.session['user_views']
    except:
        request.session['user_views'] = {}
           
    if logged_user_id:
        keychain_views_dict = request.session['user_views']
        if keychain_id in keychain_views_dict:
            if logged_user_id not in keychain_views_dict[keychain_id]:
                keychain_views_dict[keychain_id].append(logged_user_id)
            else:
                pass
        else:
            keychain_views_dict[keychain_id] = []
            keychain_views_dict[keychain_id].append(logged_user_id)
        request.session['user_views'] = keychain_views_dict

    request.session['keychain_id'] = keychain_id

    try:
        history_list = request.session['history']
        if keychain_id not in history_list and logged_user_id:
            history_list.append(keychain_id)
    except KeyError:
        request.session['history'] = []

    try:
        Keychain.objects.get(id=keychain_id)
    except ObjectDoesNotExist:
        return HttpResponse('Брелка с таким id не существует', status=404)

    context = {"keychain": Keychain.objects.get(id=keychain_id),
               "user": User.objects.all(),
               "comments": Comment.objects.order_by('-create_date').filter(keychain_id=keychain_id),
               "create_comment_form": CreateCommentForm(),
               'logged_user':
                   {'logged_user_login': logged_user_login,
                    'logged_user_id': logged_user_id,
                    'logged_user_img': logged_user_img},
               "search_form": SearchForm()
               }

    if logged_user_id != 0 and logged_user_id != '':
        context['logged_user'] = {'logged_user_login': logged_user_login,
                                  'logged_user_id': logged_user_id,
                                  'logged_user_img': logged_user_img}

    # Создание комментария

    if request.method == 'POST':
        form_content = CreateCommentForm(request.POST)
        if form_content.is_valid():

            new_comment = Comment(
                content=request.POST['content'],
                user_id=logged_user_id,
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
                category=request.POST['category'],
                description=request.POST['description'],
                user_id=request.session['logged_user_id'],
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
    return redirect('/keychain?id=' + request.session['keychain_id'] + '#comments')


def edit_comment(request):
    logged_user = User.objects.get(id=request.session['logged_user_id'])
    comment = Comment.objects.get(id=request.GET['comment_id'])
    if request.method == 'POST':

        form_content = EditCommentForm(request.POST, initial={'content': comment.content})
        if form_content.is_valid():
            edited_comment = Comment.objects.get(id=request.GET['comment_id'])
            edited_comment.content = request.POST['content']
            edited_comment.save()
            return redirect('/keychain?id=' + request.session['keychain_id'] + '#comments')
        else:
            return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": form_content,
                                                                      "logged_user": logged_user}))
    else:
        edit_comment_form = EditCommentForm(initial={'content': comment.content})
        return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": edit_comment_form,
                                                                  "logged_user": logged_user}))


def search(request):
    search_keychains = Keychain.objects.filter(title__contains=request.GET['search_input'])
    search_users = User.objects.filter(login__contains=request.GET['search_input'])
    return HttpResponse(render(request, 'search.html', {'search_keychains': search_keychains,
                                                        'search_users': search_users,
                                                        'search_title': request.GET['search_input']}))


def user_info(request):
    try:
        logged_user_id = request.session['logged_user_id']
        logged_user_login = User.objects.get(id=logged_user_id).login
        logged_user_img = User.objects.get(id=logged_user_id).user_img
    except:
        logged_user_login = ''
        logged_user_id = ''
        logged_user_img = ''

    context = {"logged_user": {"logged_user_login": logged_user_login,
                               "logged_user_img": logged_user_img,
                               "logged_user_id": logged_user_id},
               "personal_space_user_id": int(request.GET['user_id']),
               "user": User.objects.get(id=int(request.GET['user_id'])),
               "keychains": Keychain.objects.all(),
               "search_form": SearchForm()
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
    logged_user_id = request.session['logged_user_id']
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
            return redirect('/user_info?user_id=' + str(logged_user_id))
        else:
            return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': form_content}))
    else:
        edit_keychain_form = EditKeychainForm(instance=edited_keychain)
        return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': edit_keychain_form}))


def delete_keychain(request):
    logged_user_id = request.session['logged_user_id']
    deleted_keychain = Keychain.objects.get(id=request.GET['keychain_id'])
    if request.method == 'POST':
        deleted_keychain_image = deleted_keychain.img
        deleted_keychain.delete()
        remove(deleted_keychain_image.path)
        return redirect('/user_info?user_id=' + str(request.session['logged_user_id']))
    else:
        return HttpResponse(render(request, 'delete_keychain.html',
                                   {"keychain": deleted_keychain,
                                    "logged_user_id": logged_user_id}))


def history(request):
    history_list = request.session['history']

    history_keychains = []
    for history_keychain_id in history_list:
        history_keychains.append(Keychain.objects.get(id=history_keychain_id))

    return HttpResponse(render(request, 'history.html', {'history_keychains': history_keychains}))


def send_email(request):
    receiver = User.objects.get(id=request.GET['to'])
    if request.method == 'POST':
        try:
            logged_user_id = request.session['logged_user_id']
            if logged_user_id == '' or logged_user_id == 0:
                return redirect('/')
        except KeyError:
            return redirect('/')

        logged_user_login = User.objects.get(id=logged_user_id).login
        receiver = User.objects.get(id=request.GET['to'])

        form_content = SendEmailForm(request.POST)
        if form_content.is_valid():
            send_mail(
                subject='Сообщение от пользователя ' + logged_user_login,
                message=request.POST['email_text'],
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[receiver.email],
                fail_silently=False
            )
            return redirect('/keychain?id=' + request.session['keychain_id'])
    else:
        send_email_form = SendEmailForm(None)
        return HttpResponse(render(request, 'send_email.html', {'send_email_form': send_email_form,
                                                                'receiver': receiver}))


def edit_user(request):
    edited_user = User.objects.get(id=request.GET['edited_user'])
    logged_user_id = request.session['logged_user_id']
    logged_user_login = User.objects.get(id=logged_user_id).login
    logged_user_email = User.objects.get(id=logged_user_id).email
    current_user_image = edited_user.user_img

    if int(edited_user.id) != logged_user_id:
        raise PermissionDenied()
    else:

        if request.method == 'POST':
            form_content = EditUserForm(request.POST, request.FILES, instance=edited_user)
            if form_content.is_valid():

                # Проверка того, что пользователь не указал чужой логин или почту, а именно свои

                foreign_login_used = (User.objects.filter(login=request.POST['login']).exists()) and (
                            request.POST['login'] != logged_user_login)
                foreign_email_used = (User.objects.filter(email=request.POST['email']).exists()) and (
                            request.POST['email'] != logged_user_email)

                if foreign_login_used:
                    form_content.add_error('login', 'Запрещено использовать чужие данные')
                if foreign_email_used:
                    form_content.add_error('email', 'Запрещено использовать чужие данные')

                if foreign_email_used or foreign_login_used:
                    return HttpResponse(render(request, 'edit_user.html', {'edit_user_form': form_content}))

                if foreign_email_used is False and foreign_login_used is False:
                    edited_user.email = request.POST['email']
                    edited_user.login = request.POST['login']

                try:
                    uploaded_image = request.FILES['user_img']
                    remove(current_user_image.path)
                    edited_user.img = uploaded_image
                except MultiValueDictKeyError:
                    pass

                if request.POST['password'] != '':
                    edited_user.password = make_password(request.POST['password'])

                edited_user.save()
                render(request, 'user_info.html', context={
                    'logged_user': {'logged_user_login': edited_user.login,
                                    'logged_user_id': edited_user.id,
                                    'logged_user_img': edited_user.user_img}
                })

                return redirect('/user_info?user_id=' + str(logged_user_id))
            else:
                return HttpResponse(render(request, 'edit_user.html', {'edit_user_form': form_content}))

        else:
            edit_user_form = EditUserForm(instance=edited_user)
            return HttpResponse(render(request, 'edit_user.html', {'edit_user_form': edit_user_form}))
