# Import Django's cache system
from django.core.cache import cache
# Import django-redis to get direct Redis connection
from django_redis import get_redis_connection
# Import logging for tracking metrics
import logging
# Import our Property model
from .models import Property

# Set up logger for cache metrics
logger = logging.getLogger('cache_metrics')

def get_all_properties():
    """
    Get all properties with intelligent caching.
    
    This function implements the Cache-Aside pattern:
    1. Check cache first (fast lookup)
    2. If cache miss, get from database (slow query)
    3. Store in cache for future requests
    4. Return the data
    
    Cache key: 'all_properties'
    Cache TTL: 3600 seconds (1 hour)
    """
    
    # Step 1: Try to get data from Redis cache
    # cache.get() returns None if key doesn't exist
    properties = cache.get('all_properties')
    
    if properties is None:
        # Cache MISS - data not found in Redis
        print("Cache MISS: Fetching properties from database...")
        
        # Step 2: Get data from PostgreSQL database
        # This is the expensive operation we want to avoid repeating
        properties = Property.objects.all()
        
        # Convert QuerySet to list so it can be cached
        # QuerySets are lazy and can't be directly cached
        properties = list(properties)
        
        # Step 3: Store the data in Redis cache
        # cache.set(key, value, timeout_in_seconds)
        # Key: 'all_properties' - unique identifier for this cached data
        # Value: properties list - the actual data we're caching
        # Timeout: 3600 seconds = 1 hour
        cache.set('all_properties', properties, 3600)
        
        print(f"Cached {len(properties)} properties for 1 hour")
        
    else:
        # Cache HIT - data found in Redis
        print("Cache HIT: Using cached properties (fast!)")
    
    # Step 4: Return the properties (either from cache or database)
    return properties

def get_redis_cache_metrics():
    """
    Get cache performance metrics from Redis.
    
    This function analyzes how well our cache is performing by:
    1. Connecting directly to Redis
    2. Getting hit/miss statistics
    3. Calculating hit ratio (percentage of requests served from cache)
    4. Logging the results
    5. Returning metrics dictionary
    
    Hit ratio interpretation:
    - 90%+ = Excellent cache performance
    - 70-89% = Good performance
    - 50-69% = Average performance
    - <50% = Poor performance (cache not helping much)
    """
    
    try:
        # Step 1: Get direct connection to Redis
        # This bypasses Django's cache framework and talks to Redis directly
        redis_client = get_redis_connection("default")
        
        # Step 2: Get Redis server information
        # INFO command returns statistics about Redis server performance
        info = redis_client.info()
        
        # Step 3: Extract cache statistics
        # keyspace_hits = successful key lookups (cache hits)
        # keyspace_misses = failed key lookups (cache misses)
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        # Step 4: Calculate hit ratio (percentage of requests served from cache)
        if total_requests > 0:
            hit_ratio = hits / total_requests
        else:
            hit_ratio = 0.0  # No requests yet, so no ratio to calculate
            
        # Step 5: Create metrics dictionary
        metrics = {
            'hits': hits,                    # Number of cache hits
            'misses': misses,               # Number of cache misses  
            'total_requests': total_requests, # Total cache operations
            'hit_ratio': hit_ratio,         # Percentage (0.0 to 1.0)
            'hit_ratio_percent': hit_ratio * 100  # Percentage (0 to 100)
        }
        
        # Step 6: Log the metrics for monitoring
        logger.info(f"Redis Cache Metrics:")
        logger.info(f"  Cache Hits: {hits}")
        logger.info(f"  Cache Misses: {misses}")
        logger.info(f"  Total Requests: {total_requests}")
        logger.info(f"  Hit Ratio: {hit_ratio:.2%}")  # Format as percentage
        
        # Also print to console for immediate feedback
        print(f"Cache Performance: {hit_ratio:.2%} hit ratio ({hits} hits, {misses} misses)")
        
        return metrics
        
    except Exception as e:
        # Handle any connection or Redis errors gracefully
        error_msg = f"Error getting cache metrics: {e}"
        logger.error(error_msg)
        print(error_msg)
        return None

# Additional utility function to reset metrics (useful for testing)
def reset_redis_cache_stats():
    """
    Reset Redis cache statistics.
    Useful for testing or starting fresh metrics collection.
    """
    try:
        redis_client = get_redis_connection("default")
        # FLUSHDB removes all keys from current database
        # CONFIG RESETSTAT resets the hit/miss counters
        redis_client.flushdb()  # Clear all cached data
        redis_client.config_resetstat()  # Reset hit/miss statistics
        print("Cache cleared and statistics reset")
        return True
    except Exception as e:
        print(f"Error resetting cache stats: {e}")
        return False