#Valerio Bocci
#INFN Roma1
#email: valerio.bocci@roma1.infn.it
#14 November 2016 ver 1.0 simple plot CPS V.Bocci
#16 November 2016 ver 2.0 write csv file V.Bocci
#18 November 2016 ver 2.1 Scan serial port to found ArduSiPM V.Bocci
#28 November 2016 2.1.1 flush serial to have realtime reading (discarding some value) V.Bocci
#30 November 2016 2.1.2 added counts Histogram added tdc and adc data extraction code   (to be tested on field with tdc and adc enabe) V.Bocci
#13 December 2016 2.1.4 COM >= COM9 problem solved email: francesco.iacoangeli@roma1.infn.it
#19 April    2018 2.1.5 Nowe Compatible with MACOS V.Bocci
# First install the following library
# python3 -m pip install pyserial
# python3 -m pip install numpy
# python3 -m pip install matplotlib

import sys
import time
import csv
import serial
import serial.tools.list_ports
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#Scan Serial ports and found ArduSiPM
print('Serial ports available:')
ports = list(serial.tools.list_ports.comports())
for i in range (0,len(ports)):
	print(ports[i])
	pippo=str(ports[i])
	if (pippo.find('Arduino')>0):
		#serialport=pippo[0:4]
		serialport=pippo.split(" ")[0] #solve the com> com9 problem Francesco
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
# ------make plot
ydata = [0] * 60
plt.ion() # set plot to animated
plt.subplot(212)
plt.xlabel("Counts")
plt.ylabel("Number of occurrence")
plt.hist(ydata)
plt.ylim([10,40])
plt.subplot(211)
plt.ylabel("Count per sec")
plt.xlabel("sec")
line, =plt.plot(ydata,'-ob')
plt.ylim([10,40])
plt.title('ArduSiPM simple counting (V.Bocci INFN Roma1)')
plt.subplot(211)
#--end make plot
starttime=int(time.time()+.5)
filename=str(int(time.time()+.5))# CSV
filename=filename+'_Ardusipmout.csv'# CSV
with open(filename, 'w') as csvfile:# CSV
	fieldnames = ['Unix_time', 'Rate']# CSV
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=';',lineterminator='\n')# CSV
	writer.writeheader()
	while True:
		ser.reset_input_buffer() # Flush all the previous data in Serial port
		data = ser.readline().rstrip()
		#print(data)
		data=data.decode('ascii')
		#print(data)
		#-------------------------------extract data from string-------------------------
		dolpos=data.find('$')
		tpos=data.find('t')
		vpos=data.find('v')


		counts=data[dolpos+1:] #Extract counts after $ Symbol
		#print("counts=",counts)
		data=data[1:dolpos]
		if (dolpos!=0) : #More info inside the String
				if (vpos>=0): #ADC data present
				 lista=data.split('v')
				if (tpos==0):
				 lista=data.split('t') #TDC DATA present
				#if(int(counts)==len(lista)): print("num data ok")
				#print(lista)
				for i in range (0,len(lista)):
					#print(lista[i])
					pippo=str(lista[i])
					if (vpos>1) :
						vtpos=pippo.find('v')
					else:
						vtpos=len(pippo)
					#print("vtpos=",vtpos)
					if (tpos>=0) :
						tdc=pippo[0:vtpos]
					else: tdc=0
					if(vpos==0):
						adc=pippo
					elif  (vpos>=1):
						adc=pippo[vtpos+1:len(pippo)]
					else :
						adc="0"
					#print ("TDC=",tdc,"  ADC=",adc)
			#variables counts ,tdc, adc
			#----------------------------------------------------------
		unixtimestr=str(int(time.time()))
		#writer.writerow('sep=;')

		writer.writerow({'Unix_time': unixtimestr,'Rate' : counts}) # CSV

		if(  (int(time.time()+.5)%100) == 0 ):
			print ("+++++++++++++++Flush++++++++++++++++++++++")
			csvfile.flush()
		ymax = int(max(ydata))+5
		plt.ylim([0,ymax])
		ydata.append(int(counts))
		del ydata[0]
		print ("Unix time=",unixtimestr," CPS=",int(counts)," Average CPS=",sum(ydata)/len(ydata)," MAX CPS =",max(ydata) )
		#print (ydata)
		line.set_xdata(np.arange(len(ydata)))
		line.set_ydata(ydata)  # update the data
		plt.subplot(212)
		plt.cla()
		plt.xlabel("Counts")
		plt.ylabel("Number of occurrence")
		plt.hist(ydata)
		plt.draw() # update the plotser
		plt.subplot(211)
		plt.pause(1)
