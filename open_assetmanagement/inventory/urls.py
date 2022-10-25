from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),


    path('upload/', views.upload_file, name='upload_file'),
    path('download/', views.download_file, name='download'),

    path('networkscan/', views.network_scan, name='netscan'),


    path('device/<int:pk>', views.device, name='device'),
    path('device/<int:pk>/change/', views.change_device, name='change_device'),
    path('device/<int:pk>/delete/', views.delete_device, name='delete_device'),

    path('product/<int:pk>', views.product, name='product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:pk>/change/', views.change_product, name='change_product'),

    path('supplier/<int:pk>', views.supplier, name='supplier'),
    path('supplier/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    path('supplier/<int:pk>/change/', views.change_supplier, name='change_supplier'),
]
