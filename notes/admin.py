from django.contrib import admin
from notes.models import *

admin.site.register(Notebook)
admin.site.register(Note)
admin.site.register(UserProfile)
