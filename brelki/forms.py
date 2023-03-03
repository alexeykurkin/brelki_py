from django.forms import ModelForm
from . import models
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator


class RegistrationForm(ModelForm):
    email_errors = {
        'required': 'Введите адрес электронной почты',
        'invalid': 'Некорректный адрес электронной почты, пример: example@mail.ru'
    }

    login_errors = {
        'required': 'Введите логин',
    }

    password_errors = {
        'required': 'Введите пароль',
    }

    telephone_errors = {
        'required': 'Введите телефон',
        'invalid': 'Некорректный номер телефона, формат: +79999999999'
    }

    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                            error_messages=login_errors,
                            validators=[MinLengthValidator(3, 'Слишком короткий логин'),
                                        MaxLengthValidator(30, 'Слишком длинный логин')])
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                             error_messages=email_errors,
                             validators=[MinLengthValidator(5, 'Слишком короткий адрес эл. почты'),
                                         MaxLengthValidator(50, 'Слишком длинный адрес эл. почты')])
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': ' '}),
                               error_messages=password_errors,
                               validators=[MinLengthValidator(3, 'Слишком короткий пароль'),
                                           MaxLengthValidator(40, 'Слишком длинный пароль')]
                               )
    telephone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                                       error_messages=telephone_errors)
    user_img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'file-load'}))

    class Meta:
        model = models.User
        fields = ['login', 'email', 'password', 'telephone_number', 'user_img']


class AuthForm(ModelForm):
    login_errors = {
        'required': 'Введите логин'
    }

    password_errors = {
        'required': 'Введите пароль'
    }

    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                            error_messages=login_errors)

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': ' '}),
                               error_messages=password_errors)

    class Meta:
        model = models.User
        fields = ['login', 'password']


class CreateKeychainForm(ModelForm):
    title_errors = {
        'required': 'Введите имя'
    }

    description_errors = {
        'required': 'Введите пароль'
    }

    price_errors = {
        'required': 'Введите цену'
    }

    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                            error_messages=title_errors)

    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                                  error_messages=description_errors)

    price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                             error_messages=price_errors)

    img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'file-load'}))

    class Meta:
        model = models.Keychain
        fields = ['title', 'description', 'price', 'img']


class CreateCommentForm(ModelForm):
    content_errors = {
        'required': 'Заполните поле комментария!'
    }

    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'comment-input'}), error_messages=content_errors)

    class Meta:
        model = models.Comment
        fields = ['content']
