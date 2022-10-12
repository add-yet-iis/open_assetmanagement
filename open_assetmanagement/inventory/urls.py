from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('device/<int:pk>', views.device, name='device'),
    path('product/<int:pk>', views.product, name='product'),
]
