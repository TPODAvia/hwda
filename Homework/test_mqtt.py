# subscriber.py

import paho.mqtt.client as mqtt

import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker successfully!")
        client.subscribe("weather/data")  # Subscribe to the same topic used in homework.py
    else:
        print("Connection failed with result code:", rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received message on topic:", msg.topic)
    # Decode the message payload from bytes to string
    payload_str = msg.payload.decode("utf-8")
    print("Raw Payload:", payload_str)

    # If it's JSON, you can parse it (uncomment these lines if you want to process the JSON)
    try:
        payload_json = json.loads(payload_str)
        print("Parsed JSON:", json.dumps(payload_json, indent=2))
    except json.JSONDecodeError:
        print("Payload is not valid JSON.")

def main():
    # Create MQTT client instance
    client = mqtt.Client()

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker on localhost:1883
    # Make sure the broker is running, e.g. Mosquitto
    client.connect("localhost", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    client.loop_forever()

if __name__ == "__main__":
    main()
