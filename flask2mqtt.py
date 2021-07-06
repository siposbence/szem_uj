from flask import Flask, request, jsonify
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
    client.subscribe("data")
    print("subscribing to topic : "+topic)

client = mqtt.Client()
client.connect(broker, port)
client.on_connect = on_connect


app=Flask(__name__)

@app.route('/control', methods=['POST'])
def control():
    data = request.get_json(force = True)
    print('control/ called')
    print('data: ' + str(data))

    if data and 'command' in data:
        if data['command'] == 'start':
            if 'mode' in data:
                if data['mode'] == 'black':
                    print('Set eyes to black')
                    client.publish(topic,"black")
                    client.publish(topic,"black")

                elif data['mode'] == 'normal':
                    print('Set eyes to normal')
                    client.publish(topic,"normal")
                    client.publish(topic,"normal")

                elif data['mode'] == 'anime':
                    print('Set eyes to kawai')
                    client.publish(topic,"anime")
                    client.publish(topic,"anime")
            else:
                print('No mode was specified fallback to default')
                client.publish(topic,"black")
                client.publish(topic,"black")

            print('Eyes are turned on')
        elif data['command'] == 'stop':
            print('Everithing is black now')
            client.publish(topic,"off")
            client.publish(topic,"off")

        else:
            print('Invalid command is provided')
            return "error: invalid command"
            
    return "ok"

if __name__ == '__main__':
    print("Eye server started")
    app.run(host='0.0.0.0', port=5005, debug=True)