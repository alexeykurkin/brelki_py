"""brelki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('registration', views.registration),
    path('login', views.auth),
    path('logout', views.logout),
    path('keychain', views.keychain),
    path('create_keychain', views.create_keychain),
    path('delete_comment', views.delete_comment),
    path('edit_comment', views.edit_comment),
    path('search', views.search),
    path('user_info', views.user_info),
    path('edit_keychain', views.edit_keychain),
    path('delete_keychain', views.delete_keychain),
    path('history', views.history)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
