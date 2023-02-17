from django.db import models
from django.core.exceptions import ValidationError


def validate_phone(value):
    if len(value) == 12 and value[0] == '+' and value[1:].isdigit():
        pass
    else:
        raise ValidationError(
            'Неверный формат телефона, пример: +79999999999',
            params={'value': value},
        )


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=30)
    email = models.EmailField(max_length=30, error_messages='Неверный e-mail')
    password = models.CharField(max_length=200)
    reg_date = models.DateTimeField(auto_now=True)
    telephone_number = models.CharField(max_length=12, validators=[validate_phone])
    user_img = models.ImageField()

    class Meta:
        db_table = 'users'


class Keychain(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    img = models.CharField(max_length=250)

    class Meta:
        db_table = 'keychains'