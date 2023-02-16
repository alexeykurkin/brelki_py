from django.db import models


class Keychain(models.Model):

    id = models.IntegerField
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    user_id = models.IntegerField(max_length=11)
    img = models.CharField(max_length=250)

    class Meta:
        db_table = 'keychains'

    def __str__(self):
        return self.title
