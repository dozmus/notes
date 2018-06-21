from django.db import models


# class User(models.Model):
#     username = models.CharField(max_length=32, unique=True)
#     password = models.CharField(max_length=64)
#     registration_date = models.DateTimeField('registration date')


class Notebook(models.Model):
    title = models.CharField(max_length=100)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)

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
