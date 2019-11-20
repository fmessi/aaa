from datetime import datetime as dt
from sys import exit
from serial import Serial
from serial.tools.list_ports import comports
from influxdb import InfluxDBClient
from shutil import copyfile
import os.path as p
import config
# Scan Serial ports and found ArduSiPM
ports = list(comports())
ser = Serial()
for i in ports:
    i = str(i)
    if "Arduino" in i:
        ser.port = i.split(' ')[0]
        print("Found ArduSiPM in port", ser.port)
        break
else:
    print("ArduSiPM not found please connect")
    input("Press Enter to continue...")
    exit()
ser.baudrate = 115200
ser.timeout = None  # try to solve delay
if not p.isfile("config.py"):
    copyfile("config.sample.py", "config.py")
client = InfluxDBClient(config.influxdbhost,
                        config.influxdbport,
                        config.influxdbuser,
                        config.influxdbpasswd,
                        config.influxdbdb)
ser.open()
while True:
    data = ser.readline().rstrip().decode('ascii')
    dolpos = data.find('$')
    counts = int(data[dolpos + 1:])
    point = {
        "time": dt.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "measurement": "Counts",
        "fields": {
            "value": counts,
        }
    }
    #print(point)
    client.write_points([point], time_precision='s')
