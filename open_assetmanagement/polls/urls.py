from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('publishers/', views.PublisherListView.as_view(), name='pub'),
    path('<int:pk>/publishers/', views.PublisherDetailView.as_view(), name='pubdet'),
    path('contact/', views.ContactFormView.as_view(), name='contactform')
]