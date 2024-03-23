import RPi.GPIO as GPIO
import adafruit_dht
import board
import json
import time
import paho.mqtt.client as mqtt
import serial
from datetime import datetime, timedelta
import threading

button_pin = 17
DEBOUNCE_TIME = 0.5
dht_device = adafruit_dht.DHT11(board.D4)
mqtt_client = mqtt.Client()
mqtt_broker, mqtt_topic_auto, mqtt_topic_dht11_data, mqtt_topic_tid = "68.219.252.196", "auto", "/dht11_data", "/tid"
active = True

GPS_BAUD = 9600

def start_gps():
    global GPS_BAUD
    GPS = serial.Serial('/dev/serial0', GPS_BAUD, timeout=1)
    try:
        while True:
            if GPS.in_waiting > 0:
                gps_data = GPS.readline().decode('ascii', errors='ignore').strip()
                if gps_data.startswith('$GPGGA'):
                    time_utc = gps_data.split(',')[1]
                    time_utc_dansk = (datetime.strptime(time_utc, '%H%M%S.%f') + timedelta(hours=1)).strftime('%H:%M:%S')
                    mqtt_client.publish(mqtt_topic_tid, json.dumps({"time_utc": time_utc_dansk}))
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nAfslutter GPS-dataopsamling.")
        GPS.close()

def button_callback(channel):
    global active
    active = not active
    status = "genoptaget" if active else "stoppet"
    print(f"Processen er {status}")
    mqtt_client.publish(mqtt_topic_auto, f"Processen er {status}")

def publish_sensor_data():
    global active
    while True:
        if active:
            try:
                temperature = dht_device.temperature
                mqtt_client.publish(mqtt_topic_dht11_data, json.dumps({"temperature": temperature}))
            except RuntimeError as err:
                print(err.args[0])
            time.sleep(5)

def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_topic_auto)

def on_message(client, userdata, msg):
    global active
    if msg.topic == mqtt_topic_auto and msg.payload.decode() == "auto":
        button_callback(None)
        print("\nauto besked modtaget, skifter status")

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_callback, bouncetime=int(DEBOUNCE_TIME * 1000))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker)

    threading.Thread(target=publish_sensor_data).start()
    threading.Thread(target=start_gps).start()
    print("Tryk på knappen for at stoppe eller genoptage processen")
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\nProgrammet er stoppet af brugeren")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()