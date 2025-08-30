# Import Django's caching decorator
from django.views.decorators.cache import cache_page
# Import function to render templates with context data
from django.shortcuts import render
# Import HTTP response for returning JSON data
from django.http import JsonResponse
# Import our Property model
from .models import Property
# Import our caching utility functions
from .utils import get_all_properties, get_redis_cache_metrics

# @cache_page decorator caches the ENTIRE HTTP response for 15 minutes
# 60 * 15 = 900 seconds = 15 minutes
# This means Django will store the complete HTML response in Redis
@cache_page(60 * 15)  
def property_list(request):
    """
    View function that returns all properties.
    
    Now we have TWO levels of caching:
    
    LEVEL 1 - View-level caching (@cache_page):
    - Caches the complete HTTP response (HTML/JSON)
    - Lasts 15 minutes
    - Very fast for repeated identical requests
    
    LEVEL 2 - Data-level caching (get_all_properties):
    - Caches just the property data
    - Lasts 1 hour
    - Even when view cache expires, data cache might still be valid
    
    Example scenario:
    1. First request: Both caches empty, hits database
    2. Requests 2-N (within 15 min): View cache hit, super fast
    3. Request after 15 min: View cache expired, but data cache still valid
    4. Request after 1 hour: Both caches expired, hits database again
    """
    
    # Use our caching function instead of direct database query
    # This will either return cached data or fetch from database and cache it
    properties = get_all_properties()
    
    # Check if this is an API request (for JSON response)
    if request.GET.get('format') == 'json':
        # Convert properties to list of dictionaries for JSON
        properties_data = []
        for prop in properties:
            properties_data.append({
                'id': prop.id,
                'title': prop.title,
                'description': prop.description,
                'price': float(prop.price),  # Convert Decimal to float for JSON
                'location': prop.location,
                'created_at': prop.created_at.isoformat()  # Convert datetime to string
            })
        
        # Return JSON response (this will also be cached by @cache_page!)
        return JsonResponse({
            'properties': properties_data,
            'count': len(properties_data)
        })
    
    # Render HTML template with properties data
    context = {
        'properties': properties,
        'total_count': len(properties)  # len() works on list from cache
    }
    
    # Render template and return HTML response
    # This HTML response gets cached by @cache_page decorator
    return render(request, 'properties/property_list.html', context)

def cache_metrics(request):
    """
    View to display Redis cache performance metrics.
    
    This view is NOT cached because we want real-time metrics.
    Every request will get fresh statistics from Redis.
    """
    
    # Get current cache metrics from Redis
    metrics = get_redis_cache_metrics()
    
    if metrics is None:
        # Error getting metrics
        return JsonResponse({
            'error': 'Could not retrieve cache metrics',
            'status': 'error'
        }, status=500)
    
    # Return metrics as JSON for easy consumption
    return JsonResponse({
        'cache_metrics': {
            'hits': metrics['hits'],
            'misses': metrics['misses'], 
            'total_requests': metrics['total_requests'],
            'hit_ratio': f"{metrics['hit_ratio']:.4f}",  # 4 decimal places
            'hit_ratio_percent': f"{metrics['hit_ratio_percent']:.2f}%",  # 2 decimal places with %
        },
        'interpretation': {
            'performance': 'excellent' if metrics['hit_ratio'] >= 0.9 
                          else 'good' if metrics['hit_ratio'] >= 0.7
                          else 'average' if metrics['hit_ratio'] >= 0.5  
                          else 'poor',
            'recommendation': 'Cache is working well!' if metrics['hit_ratio'] >= 0.7
                            else 'Consider optimizing cache strategy'
        },
        'status': 'success'
    })