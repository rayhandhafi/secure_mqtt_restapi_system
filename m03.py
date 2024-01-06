from flask import Flask, render_template
import paho.mqtt.client as paho
import requests
import threading
from simon import SimonCipher
from speck import SpeckCipher

app = Flask(__name__)

my_speck = SpeckCipher(0x123456789ABCDEF00FEDCBA987654321)
my_simon = SimonCipher(0xABBAABBAABBAABBAABBAABBAABBAABBA)

# Initial values for M03
T1 = 0
T2 = 0

#MQTT Topics
mqttTemp1 = "test/iot/temp1"

# REST API endpoint for M02
rest_api_url_m02 = "http://192.168.18.63:5000/sensor2"

#HiveMQInit
def on_connect(client, userdata, flag, rc, properties=None):
    print("CONNACK received code %s." %rc)

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect=on_connect
client.connect("broker.hivemq.com",1883)

# Callback when a message is received from the broker for M03
def on_message(client, userdata, msg):
    global T1
    message = int(msg.payload.decode())
    T1 = my_simon.decrypt(message)
    calculate_and_display_temperature()
client.on_message = on_message
client.subscribe(mqttTemp1,qos=1)

# Function to get sensor state from M02 using REST API
def get_sensor_state_m02():
    try:
        response = requests.get(rest_api_url_m02)
        return response.json()["temperature"]
    except Exception as e:
        print(f"Error fetching sensor state from M02: {e}")
        return 0

# Function to calculate temperature difference and display the result
def calculate_and_display_temperature():
    
    # Get sensor state from M02 using REST API
    T2 = my_speck.decrypt(get_sensor_state_m02())
    final_temperature = 0
    Td = T1 - T2

    if abs(Td) > 5:
        error_notice = "Error: Temperature difference is greater than 5 degrees. Tf = 0"
        final_temperature = 0
        
    else:
        error_notice = "None"
        final_temperature = (T1 + T2) / 2
    print(f"T1 is {T1} and T2 is {T2}")
    print(f"Error Notice: {error_notice}")
    print(f"Temperature Difference: {Td}")
    print(f"Final Temperature: {final_temperature}")
    return final_temperature

# Flask route to display the final temperature
if __name__ == '__main__':
    mqtt_thread= threading.Thread(target=client.loop_forever)
    mqtt_thread.start()
    @app.route('/final_temperature', methods=['GET'])
    def final_temperature():
        formatted_temperature = f"{calculate_and_display_temperature():.2f}"  # Format the temperature with two decimal places
        return render_template('m03.html', final_temperature=formatted_temperature)
    # Run the Flask application for M03
    app.run()


