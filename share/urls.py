"""users URL Configuration

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
from django.urls import path

from . import views

app_name = 'share'

urlpatterns = [
    # Sharable note links
    path('share-note/<int:note_id>/', views.share_note, name='share-note'),
    path('new-link/<int:note_id>/', views.new_share_link, name='new-link'),
    path('edit-link/<int:note_id>/<code>/', views.edit_share_link, name='edit-link'),
    path('delete-link/<int:note_id>/<code>/', views.delete_share_link, name='delete-link'),

    # Sharable notes
    path('view-note/<int:note_id>/<code>/', views.view_shared_note, name='view-note'),
    path('download-note/<int:note_id>/<filetype>/<code>/', views.download_shared_note, name='download-note'),
    path('edit-note/<int:note_id>/<code>/', views.edit_shared_note, name='edit-note'),
    path('delete-note/<int:note_id>/<code>/', views.delete_shared_note, name='delete-note'),
]
