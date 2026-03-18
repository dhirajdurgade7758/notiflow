
from django.contrib import admin
from django.urls import path, include
from a_users.views import profile_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('notifications.urls')),
    path('api/', include('notifications.api_urls')),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name="profile"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns += [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # ... rest already exists
]