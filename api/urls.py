from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

app_name = 'api'

urlpatterns = format_suffix_patterns([
    # TODO add logging in / out
    url(r'^$', views.root_view),

    url(r'^notes/$', views.NoteList.as_view(), name='note-list'),
    url(r'^notes/(?P<pk>[0-9]+)/$', views.NoteDetail.as_view(), name='note-detail'),

    url(r'^notebooks/$', views.NotebookList.as_view(), name='notebook-list'),
    url(r'^notebooks/(?P<pk>[0-9]+)/$', views.NotebookDetail.as_view(), name='notebook-detail'),

    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),
])
