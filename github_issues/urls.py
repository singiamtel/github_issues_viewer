from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_control
from django.contrib.staticfiles.views import serve


def logout_view(request):
    """Custom logout view that handles both Django and social auth logout"""
    logout(request)
    return redirect('bye')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('', include('issues.urls')),
    path('logout/', logout_view, name='logout'),
    path('bye/', TemplateView.as_view(template_name='registration/logout.html'), name='bye'),
]
