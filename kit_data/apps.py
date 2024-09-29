from django.apps import AppConfig
import threading
from .mqtt_handler import start_mqtt_client

class KitDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kit_data'
    
    def ready(self):
        # Start the MQTT client in a separate thread
        mqtt_thread = threading.Thread(target=start_mqtt_client)
        mqtt_thread.daemon = True  # This allows Django to exit cleanly when you stop the server
        mqtt_thread.start()