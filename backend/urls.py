from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.urlpatterns import format_suffix_patterns

favicon_view = RedirectView.as_view(url='/static/images/earth.png', permanent=True)

urlpatterns = [
    path('', include('feed.urls')),
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon_view),
    path('api/', include('backend.api')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)
