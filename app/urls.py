from django.urls import path

from . import views

urlpatterns = [
    path('', views.article, name='index'),
    path(r'result/', views.article, name='result')
]