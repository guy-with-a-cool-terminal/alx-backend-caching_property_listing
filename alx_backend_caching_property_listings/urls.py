from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    # Django admin interface - accessible at /admin/
    path('admin/', admin.site.urls),
    path('properties/', include('properties.urls')),
]
