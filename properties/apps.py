# Import Django's app configuration system
from django.apps import AppConfig
import properties.signals

class PropertiesConfig(AppConfig):
    """
    Configuration class for the properties app.
    
    This tells Django how to set up and configure our app when it starts.
    """
    
    # Default field type for auto-generated primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name of this app
    name = 'properties'
    
    def ready(self):
        """
        This method runs when Django starts up and the app is ready.
        
        Perfect place to register signal handlers because:
        1. App is fully loaded
        2. Models are available
        3. Database connections are established
        4. Runs only once during startup
        """
        
        # When we import signals.py, the @receiver decorators automatically register the handlers
        
        print("Properties app ready - signal handlers registered")