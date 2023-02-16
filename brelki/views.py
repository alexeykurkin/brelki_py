from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse(render(request, 'index.html'))
