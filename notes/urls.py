"""notes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Users
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),

    # Notes
    path('new-note/', views.new_note, name='new-note'),
    # path('delete-note/<int:note_id>/', views.delete_note, name='delete-note'),
    path('new-notebook/', views.new_notebook, name='new-notebook'),
    # path('delete-notebook/<int:notebook_id>/', views.delete_notebook, name='delete-notebook'),
    #
    # # Users
    # path('login/', views.login, name='login'),
    # path('perform-login/', views.perform_login, name='perform-login'),
    # path('logout/', views.logout, name='logout'),
    # path('register/', views.register, name='register'),
]
