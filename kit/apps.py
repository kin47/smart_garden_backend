from django.apps import AppConfig
import threading
import os
from .mqtt_handler import start_mqtt_client

class KitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kit'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':  # This ensures the code runs only once
            print("Starting MQTT client...")
            mqtt_thread = threading.Thread(target=start_mqtt_client)
            mqtt_thread.daemon = True  # This allows Django to exit cleanly when you stop the server
            mqtt_thread.start()
