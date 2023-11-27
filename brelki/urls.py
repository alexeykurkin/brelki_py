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
    path('logout', views.logout_user),
    path('keychain/<int:keychain_id>', views.keychain),
    path('create_keychain', views.create_keychain),
    path('keychain/<int:keychain_id>/delete_comment/<int:deleted_comment_id>', views.delete_comment),
    path('keychain/<int:keychain_id>/edit_comment/<int:edited_comment_id>', views.edit_comment),
    path('search', views.search),
    path('user_info/<int:user_id>', views.user_info),
    path('keychain/<int:keychain_id>/edit_keychain', views.edit_keychain),
    path('keychain/<int:keychain_id>/delete_keychain', views.delete_keychain),
    path('history', views.history),
    path('send_email/<int:send_to>', views.send_email),
    path('user_info/<int:edited_user_id>/edit_user', views.edit_user)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
