from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    """Custom logout view that handles both Django and social auth logout"""
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('issues.urls')),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', logout_view, name='logout'),
]
