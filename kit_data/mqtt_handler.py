import paho.mqtt.client as mqtt
from django.utils.timezone import now

# MQTT Settings
MQTT_SERVER = "192.168.1.9"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

# 0: Connection accepted (successful connection).
# 1: Connection refused, unacceptable protocol version.
# 2: Connection refused, identifier rejected.
# 3: Connection refused, server unavailable.
# 4: Connection refused, bad username or password.
# 5: Connection refused, not authorized.

# The callback for when the client receives a connection confirmation from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

# The callback for when a message is received from the server
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Message received: {payload}")
        data = parse_sensor_data(payload)
        if data:
            save_data_to_db(data)
    except Exception as e:
        print(f"Failed to process message: {e}")

def parse_sensor_data(payload):
    """
    Example payload format: {"temperature":25.3, "humidity":60, "soil_moisture":45, "light":320}
    Adjust this method to parse your data format.
    """
    try:
        import json
        data = json.loads(payload)
        return {
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "soil_moisture": data.get("soil_moisture"),
            "light": data.get("light")
        }
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return None

def save_data_to_db(data):
    try:
        from .models import KitData
        # Create a new entry in the KitData table
        KitData.objects.create(
            temperature=data['temperature'],
            humidity=data['humidity'],
            soil_moisture=data['soil_moisture'],
            light=data['light'],
            time=now()  # Save the current timestamp
        )
        print("Data saved to the database")
    except Exception as e:
        print(f"Error saving to database: {e}")

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    
    # Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
    # It will continue running the loop until the program exits.
    client.loop_forever()
