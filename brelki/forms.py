from django.forms import ModelForm
from . import models
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, FileExtensionValidator


def validate_unique_login(value):
    if models.User.objects.filter(login=value).exists():
        raise ValidationError(
            'Логин уже занят',
            params={'value': value}
        )


def validate_unique_email(value):
    if models.User.objects.filter(email=value).exists():
        raise ValidationError(
            'Почта используется в другом аккаунте',
            params={'value': value}
        )


def validate_foreign_login(value):
    user = models.User.objects.get(login=value)

    if user:
        raise ValidationError('Логин уже занят другим пользователем', params={'value': value})


class RegistrationForm(ModelForm):
    email_errors = {
        'required': 'Введите адрес электронной почты',
        'invalid': 'Некорректный адрес электронной почты, пример: example@mail.ru'
    }

    login_errors = {
        'required': 'Введите логин'
    }

    password_errors = {
        'required': 'Введите пароль'
    }

    telephone_errors = {
        'required': 'Введите телефон',
        'invalid': 'Некорректный номер телефона, формат: +79999999999'
    }

    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                            error_messages=login_errors,
                            validators=[MinLengthValidator(3, 'Слишком короткий логин'),
                                        MaxLengthValidator(30, 'Слишком длинный логин'),
                                        validate_unique_login])

    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                             error_messages=email_errors,
                             validators=[MinLengthValidator(5, 'Слишком короткий адрес эл. почты'),
                                         MaxLengthValidator(50, 'Слишком длинный адрес эл. почты'),
                                         validate_unique_email])

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': ' '}),
                               error_messages=password_errors,
                               validators=[MinLengthValidator(3, 'Слишком короткий пароль'),
                                           MaxLengthValidator(40, 'Слишком длинный пароль')]
                               )

    telephone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                                       error_messages=telephone_errors)

    user_img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'file-load'}),
                                validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'],
                                                                   message='Файл должен быть изображением')])

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
                            validators=[MinLengthValidator(2, 'Слишком короткое название'),
                                        MaxLengthValidator(30, 'Слишком длинное название')],
                            error_messages=title_errors)

    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'create-keychain-description'}),
                                  validators=[MinLengthValidator(3, 'Слишком короткое описание'),
                                              MaxLengthValidator(100, 'Слишком длинное описание')],
                                  error_messages=description_errors)

    price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                             error_messages=price_errors)

    img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'file-load'}),
                           validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'],
                                                              message='Файл должен быть изображением')])

    class Meta:
        model = models.Keychain
        fields = ['title', 'description', 'price', 'img']


class CreateCommentForm(ModelForm):
    content_errors = {
        'required': 'Заполните поле комментария!'
    }

    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea-input'}),
                              validators=[MinLengthValidator(3, 'Слишком короткий комментарий'),
                                          MaxLengthValidator(250, 'Слишком длинный комментарий')],
                              error_messages=content_errors)

    class Meta:
        model = models.Comment
        fields = ['content']


class EditCommentForm(ModelForm):
    content_errors = {
        'required': 'Поле не должно быть пустым'
    }

    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea-input'}),
                              error_messages=content_errors,
                              validators=[MinLengthValidator(2, 'Слишком короткий комментарий'),
                                          MaxLengthValidator(250, 'Слишком длинный комментарий')])

    class Meta:
        model = models.Comment
        fields = ['content']


class SearchForm(forms.Form):
    search_input_errors = {
        'required': 'Заполните поле'
    }

    search_input = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Поиск',
                                                                 'class': 'search_input',
                                                                 'id': 'search_input'}),
                                   error_messages=search_input_errors)


EditKeychainForm = CreateKeychainForm


class SendEmailForm(forms.Form):
    email_text_errors = {'required': 'Заполните поле'}
    email_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea-input'}))


class EditUserForm(ModelForm):
    email_errors = {
        'required': 'Введите адрес электронной почты',
        'invalid': 'Некорректный адрес электронной почты, пример: example@mail.ru'
    }

    login_errors = {
        'required': 'Введите логин'
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
                               validators=[MinLengthValidator(3, 'Слишком короткий пароль'),
                                           MaxLengthValidator(40, 'Слишком длинный пароль')]
                               )

    telephone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}),
                                       error_messages=telephone_errors)

    user_img = forms.ImageField(widget=forms.FileInput(attrs={'class': 'file-load'}),
                                validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'],
                                                                   message='Файл должен быть изображением')])

    class Meta:
        model = models.User
        fields = ['login', 'email', 'password', 'telephone_number', 'user_img']
