import sqlite3
from datetime import datetime
import paho.mqtt.subscribe as subscribe
import json


def create_table():
    query = """CREATE TABLE IF NOT EXISTS konfig (datetimes TEXT, temperature REAL);"""
    try:
        conn = sqlite3.connect("database/sensordata.db")
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except sqlite3.Error as sql_e:
        print(f"sqlite error occured: {sql_e}")
    except Exception as e:
        print(f"Error occured: {e}")
    finally:
        conn.close()


create_table()


def on_message_print(client, userdata, message):
    query = """INSERT INTO konfig (datetimes, temperature) VALUES(?, ?)"""
    now = datetime.now()
    now = now.strftime("%d/%m/%y %H:%M:%S")
    json_data = json.loads(message.payload.decode())
    temperature = json_data['temperature']
    data = (now, temperature)
    
    try:
        conn = sqlite3.connect("database/sensordata.db")
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()
    except sqlite3.Error as sql_e:
        print(f"sqlite error occured: {sql_e}")
        conn.rollback()
    except Exception as e:
        print(f"Error occured: {e}")
    finally:
        conn.close()

subscribe.callback(on_message_print, "/dht11_data", hostname="68.219.252.196")
