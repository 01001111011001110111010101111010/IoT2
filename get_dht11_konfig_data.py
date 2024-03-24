import sqlite3
from datetime import datetime
from random import randint
from time import sleep

def get_konfig_data(number_of_rows):
        query = """SELECT * FROM konfig ORDER BY datetimes DESC;"""
        datetimes = []
        temperatures = []
        
        try:
            conn = sqlite3.connect("database/sensordata.db")
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchmany(number_of_rows)
            for row in reversed(rows):
                datetimes.append(row[1])
                temperatures.append(row[0])
            return datetimes, temperatures

        except sqlite3.Error as sql_e:
            print(f"sqlite error occured: {sql_e}")
            conn.rollback()
        except Exception as e:
            print(f"Error occured: {e}")
        finally:
            conn.close()
get_konfig_data(10)
