# Import Django's signal system
from django.db.models.signals import post_save, post_delete
# Import the decorator to register signal receivers
from django.dispatch import receiver
# Import Django's cache system
from django.core.cache import cache
# Import our Property model
from .models import Property

@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs AFTER a Property is saved (created or updated).
    
    Parameters:
    - sender: The model class that sent the signal (Property)
    - instance: The actual Property object that was saved
    - created: Boolean - True if this was a new object, False if updated
    - **kwargs: Any additional keyword arguments
    
    What this does:
    1. Django automatically calls this function after ANY Property.save()
    2. We delete the cached property list so next request gets fresh data
    3. This ensures cache consistency - no stale data!
    """
    
    # Delete the cached property list from Redis
    # This forces the next request to fetch fresh data from database
    cache.delete('all_properties')
    
    # Log what happened for debugging
    action = "created" if created else "updated"
    print(f"Cache invalidated: Property '{instance.title}' was {action}")
    print(f"Next request will fetch fresh data from database")

@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler that runs AFTER a Property is deleted.
    
    Parameters:
    - sender: The model class that sent the signal (Property)
    - instance: The Property object that was deleted
    - **kwargs: Any additional keyword arguments
    
    What this does:
    1. Django automatically calls this function after ANY Property.delete()
    2. We delete the cached property list since it now contains deleted property
    3. Next request will get updated list without the deleted property
    """
    
    # Delete the cached property list from Redis
    cache.delete('all_properties')
    
    # Log what happened for debugging
    print(f"Cache invalidated: Property '{instance.title}' was deleted")
    print(f"Next request will fetch updated property list")
