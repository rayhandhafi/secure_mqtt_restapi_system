import paho.mqtt.client as paho
import random
import time
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
from simon import SimonCipher
from speck import SpeckCipher

#key
key1 = "abc12@mymail.com" #128 bits
key2 = "abc12@mymail-longadd.com" #192 bits
aes_iv = "bWRHdzkzVDFJbWNB"
my_simon = SimonCipher(0xABBAABBAABBAABBAABBAABBAABBAABBA)
trunc_cipher = SpeckCipher(0x111122223333444455556666777788889999, key_size=96, block_size=48)
tiny_cipher = SpeckCipher(0x123456789ABCDEF0, key_size=64, block_size=32)


#MQTT Topics
mqttTemp1 = "test/iot/temp1"
mqttInput1 = "test/iot/input1"
pe = "test/iot/pe"
pe1 = "test/iot/pe1"

#HiveMQInit
def on_connect(client, userdata, flag, rc, properties=None):
    print("CONNACK received code %s." %rc)
client = paho.Client(client_id="", userdata=None,protocol=paho.MQTTv5)
client.connect("broker.hivemq.com", 1883)

def simulate_temperature():
    temperature = random.uniform(-1, 1) * 5 + 40
    temperature = int(temperature)
    ctT = my_simon.encrypt(temperature)
    client.publish("test/iot/temp1", payload=ctT, qos=1)
    print("T1 = ",temperature)
    print("T1 ciphertext is ", ctT)
    

# Function to handle user input and publish to M02 using MQTT
def send_user_input():
    user_input = input("Enter a message to send to M02: ")
    cipherU=AES.new(key2.encode(), AES.MODE_CBC, aes_iv.encode())
    ct_bytes2 = cipherU.encrypt(pad(user_input.encode(), AES.block_size))
    ctUI = b64encode(ct_bytes2).decode('utf-8')
    client.publish(mqttInput1, payload=ctUI,qos=1)
    print("User Input ciphertext is ", ctUI)

send_user_input()
time.sleep(2)
simulate_temperature()
print("\n\n\n")

#mess = ["A"*50,
#        "B"*100,
#        "C"*150,
#        "D"*200,
#        "E"*250]
mess = ["1"*50,"2"*100,"3"*150,"4"*200,"5"*250]
sep = ";;"

for mess in mess:
    compst= datetime.now().timestamp()
    ct = tiny_cipher.encrypt(int(mess))
    start = datetime.now().timestamp()
    msg=str(ct) + sep + str(start)
    client.publish(pe,payload=msg,qos=1)
    compend= datetime.now().timestamp()
    delay = compend - compst
    pt = trunc_cipher.decrypt(ct)
    print("Original Plaintext: ", mess)
    print("Transmission (START): ", msg)
    print("Computational Delay = ", delay)
    time.sleep(2)

client.disconnect()
