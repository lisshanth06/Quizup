"""
URL configuration for quiz_app_csi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import select_role

urlpatterns = [
    path('', select_role, name='select_role_home'),
    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('quiz/', include('quizzes.urls')),
    path('admin/', include('dashboard.urls')),
    path('admin/leaderboard/', include('leaderboard.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
