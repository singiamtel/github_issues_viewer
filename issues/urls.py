from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('select/', views.select_repository, name='select_repository'),
    path('<str:owner>/<str:repo>/', views.issues_list, name='issues_list'),
]
