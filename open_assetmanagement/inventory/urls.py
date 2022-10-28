from django.urls import path

from . import views

app_name = 'inventory'
urlpatterns = [
    path('table/', views.index, name='index'),
    path('', views.dashboard, name='dashboard'),

    # User Management
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),

    # Excel/CSV Download and Upload
    path('upload/', views.upload_file, name='upload_file'),
    path('download/', views.download_file, name='download'),

    # Import Modules
    path('networkscan/', views.network_scan, name='netscan'),
    path('s7scan/', views.s7_scan, name='s7scan'),

    # Object CRUD
    path('device/<int:pk>', views.device, name='device'),
    path('device/<int:pk>/change/', views.change_device, name='change_device'),
    path('device/<int:pk>/delete/', views.delete_device, name='delete_device'),
    path('device/create/', views.create_device, name='create_device'),

    path('product/<int:pk>', views.product, name='product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:pk>/change/', views.change_product, name='change_product'),
    path('product/create/', views.create_product, name='create_product'),

    path('supplier/<int:pk>', views.supplier, name='supplier'),
    path('supplier/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    path('supplier/<int:pk>/change/', views.change_supplier, name='change_supplier'),
    path('supplier/create/', views.create_supplier, name='create_supplier'),

    path('software/<int:pk>', views.software, name='software'),
    path('software/<int:pk>/delete/', views.delete_software, name='delete_software'),
    path('software/<int:pk>/change/', views.change_software, name='change_software'),
    path('software/create/', views.create_software, name='create_software'),
]
