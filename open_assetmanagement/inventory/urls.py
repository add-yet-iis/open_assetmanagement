from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),

    path('upload/', views.upload_file, name='upload_file'),
    path('download/', views.download_file, name='download'),

    path('networkscan/', views.network_scan, name='netscan'),


    path('device/<int:pk>', views.device, name='device'),
    path('device/<int:pk>/delete/', views.delete_device, name='delete_device'),

    path('product/<int:pk>', views.product, name='product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    path('supplier/<int:pk>', views.supplier, name='supplier'),
    path('supplier/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
]
