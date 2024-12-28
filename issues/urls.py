from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('select/', views.select_repository, name='select_repository'),
    path('<str:owner>/<str:repo>/', views.issues_list, name='issues_list'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
