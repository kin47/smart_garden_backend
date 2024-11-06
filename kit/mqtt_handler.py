import paho.mqtt.client as mqtt
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime, timedelta
from smart_garden_backend.settings import MQTT_SERVER

# MQTT Settings
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"  # Listening to sensor data
MQTT_CONTROL_TOPIC_BASE = "control/"  # Base topic for sending control commands

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
        # print(f"Message received: {payload}")
        data = parse_sensor_data(payload)
        if data:
            from .models import Kit, KitData
            # Create a new entry in the KitData table
            mac_address = data.get("mac_address")
            # Get the Kit object with the given mac_address
            kit = Kit.objects.get(mac_address=mac_address)
            save_data_to_db(data, kit)
            handle_to_send_notification(data, kit)
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
            "light": data.get("light"),
            "mac_address": data.get("mac_address")
        }
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return None

def save_data_to_db(data, kit):
    try:
        from .models import Kit, KitData
        
        KitData.objects.create(
            temperature=data['temperature'],
            humidity=data['humidity'],
            soil_moisture=data['soil_moisture'],
            light=data['light'],
            kit_id=kit,
            time=now()  # Save the current timestamp
        )
    except Exception as e:
        print(f"Error saving to database: {e}")
        
def handle_to_send_notification(data, kit):
    try:
        from authentication.models import User
        from .models import KitData, Kit
        from notification.models import Notification
        from smart_garden_backend.push_notification import send_fcm_notification
        
        users = User.objects.filter(kit_id=kit)
        current_time = timezone.now()

        # Set the time interval to prevent duplicate notifications (e.g., 1 hour)
        notification_interval = timedelta(hours=1)

        # title
        title = "Smart Garden"
        # Define the messages
        soil_moisture_message = "Độ ẩm đất đang thấp! Hãy tưới nước cho cây!"
        light_message = "Ánh sáng hơi yếu để cây có thể quang hợp! Hãy cân nhắc bật đèn!"

        # Check if a soil moisture notification was sent within the last hour
        if data['soil_moisture'] < kit.pump_threshold and not kit.is_auto_pump:
            for user in users:
                last_notification = Notification.objects.filter(
                    user=user,
                    message=soil_moisture_message
                ).order_by('-time').first()
                
                if not last_notification or (current_time - last_notification.time) > notification_interval:
                    send_fcm_notification(user.id, title, soil_moisture_message)
                    Notification.objects.create(
                        user=user,
                        message=soil_moisture_message,
                        time=current_time,
                        is_read=False
                    )

        # Check if a light notification was sent within the last hour
        if data['light'] < kit.light_threshold and not kit.is_auto_light:
            for user in users:
                last_notification = Notification.objects.filter(
                    user=user,
                    message=light_message
                ).order_by('-time').first()
                
                if not last_notification or (current_time - last_notification.time) > notification_interval:
                    send_fcm_notification(user.id, title, light_message)
                    Notification.objects.create(
                        user=user,
                        message=light_message,
                        time=current_time,
                        is_read=False
                    )

    except Exception as e:
        print(e)
        return
        
# Function to publish a control message
def publish_control_message(client, topic, message):
    try:
        result = client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Message `{message}` sent to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
    except Exception as e:
        print(f"Error publishing message: {e}")

# Control Light (Auto or Manual)
def control_light_mode(client, mode):
    topic = MQTT_CONTROL_TOPIC_BASE + "auto_light"
    payload = '1' if mode else '0'
    publish_control_message(client, topic, payload)

def control_light_manual(client, on_off):
    topic = MQTT_CONTROL_TOPIC_BASE + "manual_light"
    payload = '1' if on_off else '0'
    publish_control_message(client, topic, payload)

# Control Pump (Auto or Manual)
def control_pump_mode(client, mode):
    topic = MQTT_CONTROL_TOPIC_BASE + "auto_pump"
    payload = '1' if mode else '0'
    publish_control_message(client, topic, payload)

def control_pump_manual(client, on_off):
    topic = MQTT_CONTROL_TOPIC_BASE + "manual_pump"
    payload = '1' if on_off else '0'
    publish_control_message(client, topic, payload)

# Control Thresholds
def set_light_threshold(client, threshold):
    topic = MQTT_CONTROL_TOPIC_BASE + "light_threshold"
    publish_control_message(client, topic, str(threshold))

def set_pump_threshold(client, threshold):
    topic = MQTT_CONTROL_TOPIC_BASE + "pump_threshold"
    publish_control_message(client, topic, str(threshold))

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    
    # Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
    # It will continue running the loop until the program exits.
    client.loop_forever()
