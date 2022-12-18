"""YeeOnlineJudge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenBlacklistView

from organization import views
from organization.views.admin import MyTokenObtainPairView

urlpatterns = [
    path('user_admin/', admin.site.urls),

    path('api/org/', include('organization.urls.normal')),
    path('api/org/admin/', include('organization.urls.admin')),

    path('api/prm/', include('problem.urls.normal')),
    path('api/prm/admin/', include('problem.urls.admin')),

    path('api/sub/', include('submission.urls.normal')),
    path('api/sub/admin/', include('submission.urls.admin')),

    path('api/train/', include('training.urls.normal')),
    path('api/train/admin/', include('training.urls.admin')),

    path('api/ann/', include('announcement.urls.normal')),
    path('api/ann/admin/', include('announcement.urls.admin')),

    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('api/signup/', views.normal.register),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
