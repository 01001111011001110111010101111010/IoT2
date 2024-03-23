import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'Oguz_Hotspot'
password = 'Ahmetapak123'
mqtt_server = '68.219.252.196'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'knap_2'
topic_sub_1 = b'/dht11_data'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())