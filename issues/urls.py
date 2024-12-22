from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('repository/', views.select_repository, name='select_repository'),
    path('repository/<str:owner>/<str:repo>/issues/', views.issues_list, name='issues_list'),
] 