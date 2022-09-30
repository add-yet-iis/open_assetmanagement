from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('upload/', views.upload_file, name='upload_file'),
]
