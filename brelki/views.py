from django.shortcuts import render, HttpResponse
from brelki.models import Keychain


def index(request):
    # new_user = Keychain.objects.create(title='2', description='2', user_id=2)

    context = {'keychains': Keychain.objects.all()}

    return HttpResponse(render(request, 'index.html', context))
