import paho.mqtt.client as mqtt
import os


class MqttController:
    def __init__(self):
        self.setup()

    def setup(self):
        host = os.environ.get("INKBIRD_MQTT_HOST")
        port = int(os.environ.get("INKBIRD_MQTT_PORT", 1883))
        username = os.environ.get("INKBIRD_MQTT_USERNAME", "")
        password = os.environ.get("INKBIRD_MQTT_PASSWORD", "")

        client = mqtt.Client(client_id="inkbird")
        client.will_set("inkbird/status", payload="offline", retain=True, qos=0)

        def on_connect(client, userdata, flags, rc):
            client.publish("inkbird/status", "online", retain=True, qos=0)

        client.on_connect = on_connect

        client.username_pw_set(username, password)
        client.connect(host=host, port=port)
        client.loop_start()

        self.client = client

    def publish(self, topic, message, retain=False):
        if not self.client.is_connected():
            self.setup()
        self.client.publish(topic, message, retain=retain)


client = MqttController()
