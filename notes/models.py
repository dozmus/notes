from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db import models


class Notebook(models.Model):
    title = models.CharField(max_length=100)
    colour = RGBColorField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'notebooks'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'


class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=10000)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'notes'

    def __str__(self):
        return self.title + ' (id=' + str(self.id) + ')'
