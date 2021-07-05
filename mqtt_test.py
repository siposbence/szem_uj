import threading
import time
import paho.mqtt.client as mqtt

import json
topic="control"
broker="localhost"
port=1884
def on_connect(client, userdata, flags, rc):
    print("CONNECTED")
    print("Connected with result code: ", str(rc))
    client.subscribe(topic)
    print("subscribing to topic : "+topic)


def on_message(client, userdata, message):
    print("Data requested "+str(message.payload))


def main():
    print("WAIT for max: ",2)
    while True:
        time.sleep(1)
        client.publish(topic,"dfdfd")

### MQTT ###
client = mqtt.Client()
client.connect(broker, port)
client.on_connect = on_connect

#client.on_disconnect = on_disconnect
def subscribing():
    client.on_message = on_message
    client.loop_forever()
sub=threading.Thread(target=subscribing)
pub=threading.Thread(target=main)

### Start MAIN ###

sub.start()
pub.start()