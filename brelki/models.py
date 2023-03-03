from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


def validate_phone(value):
    if len(value) == 12 and value[0] == '+' and value[1:].isdigit():
        pass
    else:
        raise ValidationError(
            'Неверный формат телефона, пример: +79999999999',
            params={'value': value},
        )


def existing_login(value):
    if not User.objects.get(login=value):
        raise ValidationError('Такого пользователя не существует',
                              params={'value': value})


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=30)
    email = models.EmailField(max_length=30, error_messages='Неверный e-mail')
    password = models.CharField(max_length=200)
    reg_date = models.DateTimeField(auto_now=True)
    telephone_number = models.CharField(max_length=12, validators=[validate_phone])
    user_img = models.ImageField(upload_to='brelki/uploaded_images/user_images')

    REQUIRED_FIELDS = ('id', 'login', 'email', 'password', 'reg_date')

    class Meta:
        db_table = 'users'


class Keychain(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    img = models.ImageField(max_length=250, upload_to='brelki/uploaded_images/keychain_images/')
    price = models.FloatField()

    class Meta:
        db_table = 'keychains'


def correct_password(user_id, typed_password):
    if check_password(typed_password, User.objects.get(id=user_id).password):
        print('password cor! :)')


class Comment(models.Model):
    content = models.CharField(max_length=250)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
