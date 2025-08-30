# Import Django's URL routing system
from django.urls import path
# Import our views from this app
from . import views

# URL patterns for the properties app
# Each path() defines a URL route and which view function handles it
urlpatterns = [
    # When someone visits /properties/, call the property_list view function
    # name='property-list' allows us to reference this URL by name in templates
    path('', views.property_list, name='property-list'),
    path('metrics/', views.cache_metrics, name='cache-metrics'),
]