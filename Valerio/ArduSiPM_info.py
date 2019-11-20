# ArduSiPM_info
# Valerio Bocci Aprile 2018
#
# Retrive basic information from ArduSiPM
# Firmware version, Serial Number, HVCODE,ID
#
import sys
import os
import serial
import serial.tools.list_ports
import time
#os.system("ls -la")

print('Serial ports available:')
ports = list(serial.tools.list_ports.comports())
for i in range (0,len(ports)):
        print(i, end='')
        print(') ', end='')
        print(ports[i])
        pippo=str(ports[i])
        if (pippo.find('Arduino')>0):
                #serialport=pippo[0:4]
                serialport=pippo.split(" ")[0]
                print()
                print("Found ArduSiPM in port",serialport)
                print()
                notserfound=False
                break
        else : notserfound=True
if (notserfound) :
	print ("ArduSiPM not found please connect")
	input("Press Enter to continue...")
	sys.exit()

ser = serial.Serial()
ser.baudrate = 115200
ser.timeout=None #try to solve delay
ser.port = serialport
ser.open()

ser.reset_input_buffer() # Flush all the previous data in Serial port
start=time.time()
time.sleep(3)
ser.write('F\n\r'.encode())

norisposta= True
while norisposta :
        data = ser.readline().rstrip()
 #       print(data)
        data=data.decode('utf-8')


        atpos=data.find(str('@FW'))
        if ( atpos >= 0):
            version=data[atpos+3:]
            print("ArduSiPM Firmware Version:",end='')
            print(version)
            ser.write('S\n\r'.encode())
        SNpos=data.find(str('@SN'))
        if ( SNpos >= 0):
            SN=data[SNpos+3:]
            print("Serial Number:",end='')
            print(SN)
            ser.write('H\n\r'.encode())
        Hpos=data.find(str('@HV'))
        if ( Hpos >= 0):
            HVCODE=data[Hpos+3:]
            print("HVCODE:",end='')
            print(HVCODE)
 
            ser.write('I\n\r'.encode())

        Ipos=data.find(str('@I'))
        if ( Ipos >= 0):
            Ident=data[Ipos+3:]
            print("ID:",end='')
            print(Ident)
            print("Programming string: ^"+SN+"%"+HVCODE)
            norisposta= False
        if((time.time()-start )>10) : norisposta= False
        
ser.close()


