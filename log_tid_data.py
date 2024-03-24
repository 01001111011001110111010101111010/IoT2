import sqlite3
import json
import paho.mqtt.client as mqtt

def create_table():
    query = """CREATE TABLE IF NOT EXISTS konfig2 (timestamp REAL);"""
    try:
        conn = sqlite3.connect("database/tidsdata.db")
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except sqlite3.Error as sql_e:
        print(f"sqlite error occured: {sql_e}")
    except Exception as e:
        print(f"Error occured: {e}")
    finally:
        if conn:
            conn.close()

create_table()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe("/tid")
    else:
        print(f"Failed to connect to MQTT Broker with return code {rc}")

def on_message(client, userdata, msg):
    query = """INSERT INTO konfig2 (timestamp) VALUES(?)"""
    json_data = json.loads(msg.payload.decode())
    time_utc = json_data.get('time_utc')
    
    if time_utc is None:
        print(f"Invalid or missing time_utc value in message: {msg.payload.decode()}")
        return

    timestamp = time_utc
    
    data = (timestamp,)
    conn = None
    try:
        conn = sqlite3.connect("database/tidsdata.db")
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()
        print("Inserted data into database successfully")
    except sqlite3.Error as sql_e:
        print(f"sqlite error occurred: {sql_e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if conn:
            conn.close()




def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_broker = "68.219.252.196"
    mqtt_port = 1883

    try:
        mqtt_client.connect(mqtt_broker, mqtt_port)
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
