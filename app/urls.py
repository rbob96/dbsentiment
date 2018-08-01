from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('article/', views.article, name='article'),
    path('company/', views.company, name='company'),
    path('article/result/', views.article, name='result')
]