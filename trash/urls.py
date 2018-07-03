from django.urls import path

from trash import views

app_name = 'trash'

urlpatterns = [
    path('', views.trash, name='trash'),

    # Notes
    path('view-note/<int:note_id>/', views.view_note, name='view-note'),
    path(r'download-trash/<filetype>/', views.download_trash, name='download-trash'),
    path('search/', views.search, name='search'),

    # Delete selection
    path('delete-note/<int:note_id>/', views.delete_note, name='permanent-delete-note'),
    path(r'delete-notes/<note_ids>/', views.delete_notes, name='permanent-delete-notes'),
    path('delete-all/', views.delete_all_notes, name='delete-all'),

    # Restore selection
    path(r'restore-notes/<note_ids>/', views.restore_notes, name='restore-notes'),
    path('restore-note/<int:note_id>/', views.restore_note, name='restore-note'),
    path('restore-all/', views.restore_all_notes, name='restore-all'),
]
