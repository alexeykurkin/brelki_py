from ssl import SSLSession
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from brelki.models import Category, Keychain, User, Comment, Rating
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
from django.http import JsonResponse
import json
from .settings import BASE_DIR
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def get_cart():
    with open(str(BASE_DIR) + "/brelki/cart.json", 'r') as f:
        cart = json.loads(f.read())
    return cart


def update_cart(cart):
    with open(str(BASE_DIR) + "/brelki/cart.json", 'w') as f:
        json.dump(cart, f)


def get_user_cart(logged_user_id):
    cart = get_cart()
    if str(logged_user_id) in cart:
        user_cart = cart[str(logged_user_id)]
    else:
        user_cart = []

    user_cart_len = 0
    cart_sum = 0

    for kc in user_cart:
        user_cart_len += kc['count']
        cart_sum += kc['count'] * kc['price']
    
    user_cart_info = {'user_cart': user_cart, 'user_cart_len': user_cart_len, 'cart_sum': cart_sum}

    return user_cart_info


def keychain_cart_info(logged_user_id, keychain_id):
    cart_info = get_user_cart(logged_user_id)
    user_cart = cart_info['user_cart']
    user_cart_len = cart_info['user_cart_len']
    cart_sum = cart_info['cart_sum']

    hide_minus_cart = True
    hide_add_cart = False

    if user_cart:
        for kc in user_cart:
            if str(kc['id']) == keychain_id:
                hide_minus_cart = False
                hide_add_cart = True
                cart_item_count = kc['count']
                break
            hide_minus_cart = True
            cart_item_count = 0
    else:
        cart_item_count = 0
        cart_sum = 0
    
    keychain_cart_info = {'user_cart': user_cart,
                            'hide_minus_cart': hide_minus_cart, 
                            'hide_add_cart': hide_add_cart, 
                            'user_cart_len': user_cart_len,
                            'cart_item_count': cart_item_count,
                            'cart_sum': cart_sum}

    return keychain_cart_info


def index(request):

    def filter_keychains(filter_option):
        if filter_option == 'price_asc':
            keychains_list = Keychain.objects.all().order_by('price')
        elif filter_option == 'price_desc':
            keychains_list = Keychain.objects.all().order_by('-price')

        elif 'popularity' in filter_option:
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

        elif 'category' in filter_option:
            keychains_list = Keychain.objects.all().filter(category=filter_option[filter_option.find('_') + 1:])
        
        elif 'rating' in filter_option:
            get_rating = filter_option[filter_option.find('_')+1:]
            int_get_rating = int(get_rating)

            if int_get_rating in (range(1, 6)):
                from django.db.models import Avg
                keychains_list = Keychain.objects.all().annotate(kc_rating=Avg('rating__rating')).filter(kc_rating__gte=int_get_rating, kc_rating__lt=int_get_rating+1)
            elif int_get_rating == 0:
                keychains_list = Keychain.objects.exclude(id__in=list(Rating.objects.values_list('keychain_id', flat=True)))
            else:
                keychains_list = Keychain.objects.all()

        else:
            keychains_list = Keychain.objects.all()

        return keychains_list

    logged_user_id = request.user.id

    try:
        filter_option = request.GET['filter']
        if filter_option == '':
            raise NameError('Filter option is not defined')
    except:
        filter_option = ''
        keychains_list = Keychain.objects.all()

    # Фильтрация брелков
    keychains_list = filter_keychains(filter_option=filter_option)

    paginator = Paginator(keychains_list, per_page=6)
    try:
        current_page = request.GET['page']
    except KeyError:
        return redirect(f'/?page=1&filter={filter_option}')

    keychains = paginator.get_page(current_page)

    cart_info = get_user_cart(logged_user_id)

    context = {'keychains': keychains,
               'categories': Category.objects.all(),
               'users': User.objects.all(),
               'filter_option': filter_option,
               "search_form": SearchForm(),
               'cart_info': {
                   'cart': cart_info['user_cart'],
                   'user_cart_len': cart_info['user_cart_len'],
                   'cart_sum': cart_info['cart_sum']
               },
               'user': request.user
               }

    if request.GET:
        search_content = SearchForm(request.GET)
        if search_content.is_valid():
            return redirect('/search?search_input=' + request.GET['search_input'])

    if request.method == 'POST':
        if request.POST['action'] == 'delete':
            with open(str(BASE_DIR) + "/brelki/cart.json", 'r') as f:
                ucart = json.load(f)

            cart[str(logged_user_id)] = []

            with open(str(BASE_DIR) + "/brelki/cart.json", 'w') as f:
                cart = json.dump(cart, f)

            return JsonResponse({'response': 'success'})

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
        form_content = AuthForm(data=request.POST)
        user = authenticate(login=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            else:
                return redirect('/')
        else:
            messages.add_message(request, messages.INFO, 'Неверный логин или пароль')
            return HttpResponse(render(request, 'login.html', {'auth_form': form_content}))
    else:
        auth_form = AuthForm(None)
        return HttpResponse(render(request, 'login.html', {'auth_form': auth_form}))


def logout_user(request):
    logout(request)
    return redirect('/')


def keychain(request, keychain_id):

    def update_keychain_views(logged_user_id):
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

        else:
            keychain_views_dict = {}
        
        return keychain_views_dict
    
    def update_keychain_history(logged_user_id):
        try:
            history_list = request.session['history']
            if keychain_id not in history_list and logged_user_id:
                history_list.append(keychain_id)
        except KeyError:
            request.session['history'] = []

    logged_user_id = request.user.id

    try:
        Keychain.objects.get(id=keychain_id)
    except ObjectDoesNotExist:
        return HttpResponse('Брелка с таким id не существует', status=404)

    request.session['user_views'] = update_keychain_views(logged_user_id)

    update_keychain_history(logged_user_id)
    update_keychain_views(logged_user_id)

    keychain_cart_state = keychain_cart_info(logged_user_id, str(keychain_id))

    # Получение рейтинга брелка
    try:
        keychain_rating = list(Rating.objects.filter(keychain_id=keychain_id).values_list('rating', flat=True))
        import statistics
        keychain_rating_float = round(statistics.mean(keychain_rating), 2)
        keychain_rating_count = len(keychain_rating)
    except:
        keychain_rating_float = 0
        keychain_user_rating = 0
        keychain_rating_count = 0

    try:
        keychain_user_rating = Rating.objects.get(user_id=logged_user_id, keychain_id=keychain_id).rating
    except:
        keychain_user_rating = 0


    context = {"keychain": Keychain.objects.get(id=keychain_id),
               "user": User.objects.all(),
               "comments": Comment.objects.order_by('-create_date').filter(keychain_id=keychain_id),
               "create_comment_form": CreateCommentForm(),
               'cart_info': {
                   "cart": keychain_cart_state['user_cart'],
                   "user_cart_len": keychain_cart_state['user_cart_len'],
                   "hide_minus_cart": keychain_cart_state['hide_minus_cart'],
                   "hide_add_cart": keychain_cart_state['hide_add_cart'],
                   "cart_item_count": keychain_cart_state['cart_item_count'],
                   "cart_sum": keychain_cart_state['cart_sum']
               },
               "rating": {
                    "keychain_rating_float": keychain_rating_float,
                    "keychain_user_rating": keychain_user_rating,
                    "keychain_rating_count": keychain_rating_count
               },
               "user": request.user,
               "search_form": SearchForm()
               }

    # Создание комментария

    if request.method == 'POST':

        if 'action' in request.POST:

            if request.POST['action'] == 'plus':
                
                cart = get_cart()
                if str(logged_user_id) not in cart:
                    cart[str(logged_user_id)] = []

                new_keychain = True
                for kc in cart[str(logged_user_id)]:
                    # расчёт суммы брелков в корзине
                    if int(keychain_id) == kc['id']:
                        kc['count'] += 1
                        new_keychain = False
                        break

                if new_keychain:
                    cart[str(logged_user_id)].append({
                        "id": int(keychain_id),
                        "title": str(Keychain.objects.get(id=keychain_id).title),
                        "count": 1,
                        "price": Keychain.objects.get(id=keychain_id).price,
                        "img": str(Keychain.objects.get(id=keychain_id).img)
                    })

                update_cart(cart)

                user_cart = keychain_cart_info(logged_user_id, str(keychain_id))

                return JsonResponse({
                    'id': keychain_id,
                    'title': Keychain.objects.get(id=keychain_id).title,
                    'img': str(Keychain.objects.get(id=keychain_id).img),
                    'cart_action': 'add',
                    'user_cart_len': user_cart['user_cart_len'],
                    'cart_item_count': user_cart['cart_item_count'],
                    'cart_sum': user_cart['cart_sum']
                })

            elif request.POST['action'] == 'minus':
                cart = get_cart()

                for kc in cart[str(logged_user_id)]:
                    if int(keychain_id) == kc['id']:
                        if kc['count'] == 1:
                            cart[str(logged_user_id)].remove(kc)
                        else:
                            kc['count'] -= 1
                            break

                update_cart(cart)

                user_cart = keychain_cart_info(logged_user_id, str(keychain_id))

                return JsonResponse({'response': 'success',
                                     'id': keychain_id,
                                     'cart_action': 'substract',
                                     'user_cart_len': user_cart['user_cart_len'],
                                     'cart_item_count': user_cart['cart_item_count'],
                                     'cart_sum': user_cart['cart_sum']
                                     })

            elif request.POST['action'] == 'delete':
                cart = get_cart()

                cart[str(logged_user_id)] = []

                update_cart(cart)

                return JsonResponse({'response': 'success',
                                     'cart_action': 'clear'})
        
        elif 'rating' in request.POST:

            if request.POST['rating'] == 'clear-rating':
                delete_rate = Rating.objects.get(user_id=logged_user_id, keychain_id=keychain_id)
                delete_rate.delete()

            elif int(request.POST['rating']) in range(1, 6):

                try:
                    current_rate = Rating.objects.get(user_id=logged_user_id, keychain_id=keychain_id)
                    current_rate.rating = request.POST['rating']
                    current_rate.save()
                except:
                    new_rate = Rating(
                        user_id=logged_user_id,
                        keychain_id=keychain_id,
                        rating=request.POST['rating']
                    )
                    new_rate.save()

            return HttpResponseRedirect("/keychain/" + str(keychain_id) + '#keychain_image')

        else:
            form_content = CreateCommentForm(request.POST)
            if form_content.is_valid():

                new_comment = Comment(
                    content=request.POST['content'],
                    user_id=logged_user_id,
                    keychain_id=keychain_id
                )
                new_comment.save()
                return HttpResponseRedirect("/keychain/" + str(keychain_id) + '#comments')

            else:
                context["create_comment_form"] = form_content
                return HttpResponse(render(request, 'keychain.html', context))
    else:
        context['create_comment_form'] = CreateCommentForm(None)
        return HttpResponse(render(request, 'keychain.html', context))

    return HttpResponse(render(request, 'keychain.html', context))


@login_required
def create_keychain(request):
    if request.method == 'POST':
        form_content = CreateKeychainForm(request.POST, request.FILES)
        if form_content.is_valid():
            new_keychain = Keychain(
                title=request.POST['title'],
                category=request.POST['category'],
                description=request.POST['description'],
                user_id=request.user.id,
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


@login_required
def delete_comment(request, keychain_id, deleted_comment_id):
    try:
        deleted_comment = Comment.objects.get(id=deleted_comment_id)
    except ObjectDoesNotExist:
        return HttpResponse('Такого комментария не существует', status=404)
    
    try:
        origin_page = request.GET['from']
    except MultiValueDictKeyError:
        origin_page = 'undefined'

    logged_user_id = request.user.id

    if (logged_user_id != deleted_comment.user.id):
        raise PermissionDenied()
    
    comment_user_id = deleted_comment.user.id
    deleted_comment.delete()

    if origin_page == 'keychain':
        return redirect('/keychain/' + str(keychain_id) + '#comments')
    elif origin_page == 'user_info':
        return redirect('/user_info/' + str(comment_user_id) + '#user_comments')
    else:
        return redirect('/')


@login_required
def edit_comment(request, keychain_id, edited_comment_id):
    user = User.objects.get(id=request.user.id)

    try:
        origin_page = request.GET['from']
    except MultiValueDictKeyError:
        origin_page = 'undefined'

    try:
        comment = Comment.objects.get(id=edited_comment_id)
    except ObjectDoesNotExist:
        return HttpResponse('Такого комментария не существует', status=404)

    if comment.user.id != user.id:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form_content = EditCommentForm(request.POST, initial={'content': comment.content})
        if form_content.is_valid():
            edited_comment = comment
            comment_user_id = comment.user.id
            edited_comment.content = request.POST['content']
            edited_comment.save()

            if origin_page == 'keychain':
                return redirect('/keychain/' + str(keychain_id) + '#comments')
            elif origin_page == 'user_info':
                return redirect('/user_info/' + str(comment_user_id) + '#user_comments')
            else:
                return redirect('/')
            
        else:
            return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": form_content,
                                                                      "user": user}))
    else:
        edit_comment_form = EditCommentForm(initial={'content': comment.content})
        return HttpResponse(render(request, 'edit_comment.html', {"edit_comment_form": edit_comment_form,
                                                                  "user": user}))


def search(request):
    search_keychains = Keychain.objects.filter(title__contains=request.GET['search_input'])
    search_users = User.objects.filter(login__contains=request.GET['search_input'])
    return HttpResponse(render(request, 'search.html', {'search_keychains': search_keychains,
                                                        'search_users': search_users,
                                                        'search_title': request.GET['search_input']}))


def user_info(request, user_id):
    logged_user_id = request.user.id
    cart_info = get_user_cart(logged_user_id)

    try:
        personal_space_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return HttpResponse('Такого пользователя не существует', status=404)

    context = {
        "personal_space_user": personal_space_user,
        "keychains": Keychain.objects.all(),
        "search_form": SearchForm(),
        'cart_info': 
            {
                'cart': cart_info['user_cart'],
                'user_cart_len': cart_info['user_cart_len'],
                'cart_sum': cart_info['cart_sum']
            },
        'user': request.user
        }

    try:
        user_keychains = Keychain.objects.filter(user_id=user_id)
        user_comments = Comment.objects.filter(user_id=user_id)
    except ObjectDoesNotExist:
        user_keychains = {}
        user_comments = {}

    context['user_keychains'] = user_keychains
    context['user_comments'] = user_comments

    return HttpResponse(render(request, 'user_info.html', context))


@login_required
def edit_keychain(request, keychain_id):
    edited_keychain = Keychain.objects.get(id=keychain_id)
    current_keychain_image = edited_keychain.img
    logged_user_id = request.user.id

    if edited_keychain.user.id != logged_user_id:
        raise PermissionDenied()

    if request.method == 'POST':
        form_content = EditKeychainForm(request.POST, request.FILES, instance=edited_keychain)
        if form_content.is_valid():
            edited_keychain.title = request.POST['title']
            edited_keychain.description = request.POST['description']
            edited_keychain.price = request.POST['price']
            edited_keychain.category = request.POST['category']
            try:
                uploaded_image = request.FILES['img']
                remove(current_keychain_image.path)
                edited_keychain.img = uploaded_image
            except MultiValueDictKeyError:
                pass

            edited_keychain.save()
            return redirect('/user_info/' + str(logged_user_id))
        else:
            return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': form_content}))
    else:
        edit_keychain_form = EditKeychainForm(instance=edited_keychain, initial={'category': edited_keychain.category})
        return HttpResponse(render(request, 'edit_keychain.html', {'edit_keychain_form': edit_keychain_form}))

@login_required
def delete_keychain(request, keychain_id):
    logged_user_id = request.user.id
    deleted_keychain = Keychain.objects.get(id=keychain_id)
    if request.method == 'POST':
        keychain_history = request.session['history']
        if str(deleted_keychain.id) in keychain_history:
            keychain_history.remove(deleted_keychain.id)
            
        request.session['history'] = keychain_history
        try:
            deleted_keychain_image = deleted_keychain.img
            deleted_keychain.delete()
            remove(deleted_keychain_image.path)
        except:
            pass

        return redirect('/user_info/' + str(request.user.id))
    else:
        return HttpResponse(render(request, 'delete_keychain.html',
                                   {"keychain": deleted_keychain,
                                    "logged_user_id": logged_user_id}))


@login_required
def history(request):
    try:
        history_list = request.session['history']
    except KeyError:
        history_list = []

    history_keychains = []
    for history_keychain_id in history_list:
        history_keychains.append(Keychain.objects.get(id=history_keychain_id))

    return HttpResponse(render(request, 'history.html', {'history_keychains': history_keychains}))


@login_required
def send_email(request, send_to):
    receiver = User.objects.get(id=send_to)
    if request.method == 'POST':
        try:
            logged_user_id = request.user.id
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
            return redirect('/keychain/' + request.session['keychain_id'])
    else:
        send_email_form = SendEmailForm(None)
        return HttpResponse(render(request, 'send_email.html', {'send_email_form': send_email_form,
                                                                'receiver': receiver}))


@login_required
def edit_user(request, edited_user_id):
    edited_user = User.objects.get(id=edited_user_id)
    logged_user_id = request.user.id

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
                login(request, edited_user)
                render(request, 'user_info.html', context={
                    'user': request.user
                })

                return redirect('/user_info/' + str(logged_user_id))
            else:
                return HttpResponse(render(request, 'edit_user.html', {'edit_user_form': form_content}))

        else:
            edit_user_form = EditUserForm(instance=edited_user)
            return HttpResponse(render(request, 'edit_user.html', {'edit_user_form': edit_user_form}))
