from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import AbstractBaseUser

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


class User(AbstractBaseUser):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=200)
    reg_date = models.DateTimeField(auto_now=True)
    telephone_number = models.CharField(max_length=12, validators=[validate_phone])
    user_img = models.ImageField(upload_to='brelki/uploaded_images/user_images')

    USERNAME_FIELD = "login"
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ('id', 'email', 'password', 'reg_date')
    
    from django.contrib.auth.models import UserManager
    objects = UserManager()

    class Meta:
        db_table = 'users'

class Category(models.Model):
    category = models.CharField(primary_key=True, max_length=15)
    REQUIRED_FIELDS = ('category')

    class Meta:
        db_table = 'categories'

class Keychain(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=30)
    category = models.CharField(max_length=15)
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
    id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=250)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    keychain = models.ForeignKey(Keychain, db_column='keychain_id', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        

class Rating(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    keychain = models.ForeignKey(Keychain, db_column='keychain_id', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, db_column='rating')
    UniqueConstraint(fields=(user, keychain), name='unique_rating')

    class Meta:
        db_table = 'rating'
    