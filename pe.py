import paho.mqtt.client as paho
from datetime import datetime
from simon import SimonCipher
from speck import SpeckCipher

#trunc_cipher = SimonCipher(0x111122223333444455556666777788889999, key_size=96, block_size=48)
#tiny_cipher = SimonCipher(0x123456789ABCDEF0, key_size=64, block_size=32)
trunc_cipher = SpeckCipher(0x111122223333444455556666777788889999, key_size=96, block_size=48)
tiny_cipher = SpeckCipher(0x123456789ABCDEF0, key_size=64, block_size=32)

def on_connect(client, userdata, flag, rc, properties=None):
    print("CONNACK received code %s." %rc)

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect=on_connect
client.connect("broker.hivemq.com",1883)


sep = ";;"
def on_message(client, userdata, msg):
    msg = msg.payload.decode("utf-8")
    timeSend = msg.split(sep)[1]
    end = datetime.now().timestamp()
    delay = end - float(timeSend)
    ct = msg.split(sep)[0]
    pt = tiny_cipher.decrypt(int(ct))
    print("transmission delay = ", delay, " seconds\n")
    print("Ciphertext: ", ct)
    print("Recovered Simon Plaintext: ", pt, "\n")

client.on_message = on_message
client.subscribe("test/iot/pe", qos=1)
client.loop_forever()