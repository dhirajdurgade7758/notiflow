
from django.contrib import admin
from django.urls import path, include
from a_users.views import profile_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('notifications.urls')),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name="profile"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)