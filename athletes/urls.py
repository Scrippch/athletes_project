from django.urls import path
from . import views

app_name = 'athletes'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_athlete, name='add_athlete'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
]