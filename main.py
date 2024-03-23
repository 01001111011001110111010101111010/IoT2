from machine import Pin
import time
import network
from umqtt.simple import MQTTClient
import ujson
import neopixel

wifi_ssid = "Oguz_Hotspot"
wifi_password = "Ahmetapak123"

mqtt_broker = "68.219.252.196"
mqtt_topic = b'knap_2'
mqtt_topic_dht11 = b'/dht11_data'

magnet_sensor_pin = Pin(21, Pin.IN, Pin.PULL_UP)

dirPin = Pin(17, Pin.OUT)
stepPin = Pin(16, Pin.OUT)
motorSpeed = 0.001

NUM_PIXELS = 12
PIXEL_PIN = 32
np = neopixel.NeoPixel(Pin(PIXEL_PIN), NUM_PIXELS)

current_position = 0

def step_motor(steps, direction):
    dirPin.value(direction)
    for _ in range(abs(steps)):
        stepPin.value(1)
        time.sleep(motorSpeed)
        stepPin.value(0)
        time.sleep(motorSpeed)

def move_to_position(new_position):
    global current_position
    positions = [0, 400, 600, 800]
    steps_to_move = positions[new_position] - current_position
    
    if steps_to_move > 0:
        direction = 1
    else:
        direction = 0
        steps_to_move = -steps_to_move
    
    step_motor(steps_to_move, direction)
    current_position = positions[new_position]

    set_neopixel_color(new_position)

def mqtt_callback(topic, msg):
    print("Received MQTT message on topic", topic, ":", msg.decode())
    if topic == mqtt_topic:
        try:
            received_position = int(msg.decode())
            if received_position in [0, 1, 2, 3]:
                move_to_position(received_position)
            else:
                print("Received an invalid position:", received_position)
        except ValueError:
            print("Received message is not a valid position")
    elif topic == mqtt_topic_dht11:
        try:
            data = ujson.loads(msg.decode())
            if 'temperature' in data:
                temperature = data['temperature']
                adjust_position_based_on_temperature(temperature)
        except ValueError:
            print("Error parsing JSON from DHT11 data")
            
def adjust_position_based_on_temperature(temperature):
    if temperature < 20:
        move_to_position(3)
    elif 20 <= temperature < 25:
        move_to_position(2)
    elif 25 <= temperature < 30:
        move_to_position(1)
    elif temperature > 30:
        move_to_position(0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass
    print('WiFi connected:', wlan.ifconfig())

def connect_mqtt():
    client = MQTTClient("esp32", mqtt_broker)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(mqtt_topic)
    client.subscribe(mqtt_topic_dht11)
    print("Connected to MQTT Broker and subscribed to topics")
    return client

def clear_neopixel():
    for i in range(NUM_PIXELS):
        np[i] = (0, 0, 0)
    np.write()

def set_neopixel_color(position):
    clear_neopixel()
        
    if position == 3:
        color = (13, 0, 0)
    elif position == 2:
        color = (12, 1, 1)
    elif position == 1:
        color = (12, 3, 3)
    elif position == 0:
        color = (0, 0, 13)
        
    for i in range(NUM_PIXELS):
        np[i] = color
        
    np.write()
    
def check_magnet_sensor():
     global last_magnet_state
     current_state = magnet_sensor_pin.value()
     if last_magnet_state == 0 and current_state == 1:
         print("Window opened, moving to position 0.")
         move_to_position(0)
     if last_magnet_state == 1 and current_state == 0:
         print("Window is closed.")
     last_magnet_state = current_state

def main():
    clear_neopixel()
    connect_wifi()
    mqtt_client = connect_mqtt()
    global last_magnet_state
    last_magnet_state = magnet_sensor_pin.value()
    
    while True:
        mqtt_client.check_msg()
        check_magnet_sensor()
        
        time.sleep(1)

if __name__ == "__main__":
    main()