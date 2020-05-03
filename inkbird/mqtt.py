import paho.mqtt.client as mqtt
import os


class MqttController:
    def __init__(self):
        host = os.environ.get("INKBIRD_MQTT_HOST")
        port = int(os.environ.get("INKBIRD_MQTT_PORT", 1883))

        client = mqtt.Client(client_id="inkbird")
        client.will_set("inkbird/status", payload="offline", retain=True, qos=0)
        client.connect(host=host, port=port)
        client.publish("inkbird/status", "online", retain=True, qos=0)

        self.client = client
    
    def publish(self, topic, message):
        self.client.publish(topic, message)

client = MqttController()
