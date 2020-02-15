from django.urls import path

from . import views

app_name = 'client'
urlpatterns = [
    path('', views.client_view, name='base'),
    path('<path:req_path>', views.client_view, name='path'),
]
