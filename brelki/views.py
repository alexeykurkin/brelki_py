from django.shortcuts import render, HttpResponse
from brelki.models import Keychain, User
from .forms import RegistrationForm
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password, make_password


def index(request):
    context = {'keychains': Keychain.objects.all(), 'users': User.objects.all()}
    return HttpResponse(render(request, 'index.html', context))


def registration(request):

    if request.method == 'POST':
        form_content = RegistrationForm(request.POST, request.FILES)
        print(request.FILES)
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



