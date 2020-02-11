
#!/usr/bin/env python3

'''
 --------------------------------------------------------------------
|              aaa - ArduSiPM Acquisition & Analysis                 |
 --------------------------------------------------------------------
| Python libraries for the ArduSiPM                                  |
| project web: https://sites.google.com/view/particle-detectors/home |
| code repository: https://github.com/fmessi/aaa.git                 |
|                                                                    |
| history:                                                           |
| 191119 - F.Messi - import info script from V.Bocci original code   |
|                    load of data-file from F.Curti DAQ              |
 --------------------------------------------------------------------
'''

import sys
import os
import time
from datetime import datetime, timedelta
import csv
import serial
import serial.tools.list_ports
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import Utility as ut

## import aaa_scripts
import a-load as lf
import a-analysis as an

def menu_long():
    print("\n ========================= ")
    print("     WELCOME TO ArduSiPM   ")
    print(" ========================= ")
    print(" type menu() for this menu \n")
    print(" available functions are:  ")
    print("   - Info_ASPM():                Retrive basic information from ArduSiPM ")
    print("   - Acquire_ASPM():        Open connection and start acquisition")
    print("   - Save_Data():           Save recorded data on a file")
    print("   - ")
    print("   - lf.Load_Curti_xlsx():     Load data from xlsx output file")
    print("   - lf.LoadMerge_xlsx():      Load all files from a folder (xlsx)")
    print("   - lf.Load_csv():            Load data from CVS output file")
    print("   - lf.LoadMerge_cvs():      Load all files from a folder (cvs)")
    print("   - ")
    print("   - Plot_ADC():            1D plot of ADC spectra")
    print("   - ")
    print("   - RunIt():               ")
    print("   - RunLoop():")
    print("   - Acquire_ASPM()")
    print("   - ")
    print("   - menu_Long()")
    print(" ========================= \n")

def menu():
    print("\n ========================= ")
    print("     WELCOME TO ArduSiPM   ")
    print(" ========================= ")
    print(" type menu() for this menu \n")
    print(" available functions are:  ")
    print("   - Info_ASPM()")
    print("   - lf.Load_csv(filename=, debug=)")
    print("   - lf.LoadMerge_cvs(directory=, InName=, OutName=, debug=)")
    print("   - ")
    print("   - Plot_ADC(dati, binsize=16, hRange=[0,4000])")
    print("   - ")
    print("   - RunIt(duration_acq=0, file_par=)               ")
    print("   - RunLoop(duration_acq, nLoops, file_par)")
    print("   - ")
    print("   - menu_Long()")
    print(" ========================= \n")

def interactive():
    print(" Interactive IPython shell ")
    print(" ========================= ")
    print(" Quick command usage:")
    print("  - 'who' or 'whos' to see all (locally) defined variables")
    print("  - if the plots are shown only as black area, run '%gui qt'")
    print("  - to make cmd prompt usable while plots are shown use 'plt.ion()' for interactive mode")
    print("    or run 'plt.show(block=False)' to show them")
    import IPython
    IPython.embed()



'''==================
     Plotting
=================='''
#def Plot_ADC(dati, binsize=16, hRange=[0,4095], label='no_label', weights=None, log=True, ylabel=None, fig=1):
def Plot_ADC(dati, binsize=1, hRange=[0,1000], label='no_label', weights=None, log=True, ylabel=None, fig=1):
    '''
    SCOPE: fast plot of ADC spectra
    INPUT: data
    OUTPUT: print info on screen and histo parameters
    '''
    nBin = int((hRange[1]-hRange[0])/binsize)
    title = 'ADC spectra'
    xlabel = 'ADC channel'
    ylabel = ylabel
    n, bins, patches = ut.Plot1D(dati.ADC, nBin=nBin, R=hRange, title=title, xlabel=xlabel, label=label, log=log, weights=weights, c=fig)
    return n, bins, patches

def Plot_CPS(dati, binsize=1, hRange=[0,100], label='no_label', weights=None, log=True, ylabel=None, fig=1):
    '''
    SCOPE: fast plot of ADC spectra
    INPUT: data
    OUTPUT: print info on screen and histo parameters
    '''
    nBin = int((hRange[1]-hRange[0])/binsize)
    title = 'CPS distribution'
    xlabel = 'CPS'
    ylabel = ylabel
    n, bins, patches = ut.Plot1D(dati.CPS, nBin=nBin, R=hRange, title=title, xlabel=xlabel, label=label, log=log, weights=weights, c=fig)
    print(f'CPS mean of {label} is {dati.CPS.mean()}')
    return n, bins, patches

'''==================
     ArduSiPM interfacing
=================='''
def Info_ASPM():
    '''
    SCOPE: call to the original info script from V.Bocci
    INPUT: none
    OUTPUT: print info on screen
    '''
    sys.path.append('Valerio/')
    import ArduSiPM_info.py

def Search_ASPM(baudrate=115200, timeout=None, debug=False):
    '''
    SCOPE: search for ArduSiPM
    NOTE: copied and adapted from the original script from V.Bocci
    INPUT: none
    OUTPUT: string with serial name
    '''
    #Scan Serial ports and found ArduSiPM
    if(debug): print('Serial ports available:')
    ports = list(serial.tools.list_ports.comports())
    for i in range (0,len(ports)):
        if(debug): print(ports[i])
        pippo=str(ports[i])
        if (pippo.find('Arduino')>0):
            serialport=pippo.split(" ")[0] #TODO: ? solve the com> com9 problem Francesco
            print(f"Found ArduSiPM in port {serialport}")
            return(str(serialport))
        else :
            print ("no ArduSiPM, looking more...")

def Apri_Seriale():
	ser = serial.Serial()
	ser.baudrate = 115200
	ser.timeout=None
	ser_num = Search_ASPM()
	if (ser_num):
	        ser.port = ser_num
	        ser.open()
	        time.sleep(1)
	else:
	        print('ArduSiPM not found please connect')
	        return(0)
	return(ser)

def Scrivi_Seriale(comando, ser):
    if(ser):
        ser.write(str('m').encode('utf-8'))
        time.sleep(2)
        ser.write(str(comando).encode('utf-8'))
        time.sleep(2)
        ser.write(str('e').encode('utf-8'))
        print(f'wrote on serial {comando}')
        time.sleep(0.5)

def SetThreshold(threshold, ser):
    if(ser):
        ser.write(str('m').encode('utf-8'))
        time.sleep(2)
        ser.write(str('t').encode('utf-8'))
        time.sleep(2)
        #ser.write(threshold.to_bytes(4, 'little'))
        #ser.write(b'10')
        ser.write(str(threshold).encode('utf-8'))
        time.sleep(4)
        ser.write(str('e').encode('utf-8'))
        time.sleep(2)


'''==================
     Data acquisition
=================='''
def Save_Data(data, file_name='my_data.csv'):
    '''
    SCOPE:
    INPUT: file name and data in binary format
    OUTPUT:
    '''
    with open(file_name, 'w') as file:
        #writer = csv.writer(file, delimiter=',')
        for line in data:
            file.write(line)#.decode('ascii'))
            file.write(',')

def Acquire_ASPM(duration_acq, ser, debug=False):
    '''
    SCOPE:
    INPUT: duration in seconds
    OUTPUT: a DataFraMe with the data
    '''
    lista = []
    start_acq_time = datetime.now()
    stop_acq_time = start_acq_time + timedelta(seconds=duration_acq-1)
    acq_time = datetime.now()
    while(acq_time < stop_acq_time):
        acq_time = datetime.now()
        #print(acq_time.strftime('%H:%M:%S'))
        ser.reset_input_buffer() # Flush all the previous data in Serial port
        data = ser.readline().rstrip()
        tdata = f"u{acq_time.strftime('%y%m%d%H%M%S.%f')}{data.decode('ascii')}"
        if(debug): print(tdata)
        lista.append(tdata)
        time.sleep(0.2)
    return(lista)

def RunIt(duration_acq=0, file_par='RawData', threshold=200, debug=False):
    '''
    SCOPE:
    NOTE: copied and adapted from the original script from V.Bocci
    INPUT:
    OUTPUT:
    '''
    start_time = datetime.now()
    stopat = start_time+timedelta(seconds=duration_acq)
    ## serial connection
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.timeout=None #try to solve delay
    ser_num = Search_ASPM()
    if (ser_num):
        ser.port = ser_num
        ser.open()
        time.sleep(1)
    else:
        print('ArduSiPM not found please connect')
        return(0)
    ## acquisition
    #ser.write(b'a') # enable ADC
    #ser.write(b'd') # enable TDC
    #ser.write(b'h75') # set HV
    #Scrivi_Seriale(b's3', ser)
    #Scrivi_Seriale(b'@', ser)
    #time.sleep(0.5)
    #ser.write(b'@')
    #time.sleep(0.5)
    ser.write(b'#')
    time.sleep(0.5)
    SetThreshold(threshold, ser)
    ser.write(b'$')
    time.sleep(4)
    #ser.write(b'#') ## ADC+CPS
    ser.write(b'@') ## TDC+ADC+CPS
    time.sleep(0.5)
    print(f'Acquiring now... this run will stop at {stopat}')
    data = Acquire_ASPM(duration_acq, ser, debug=debug)
    print('SAVING DATA...')
    Save_Data(data, f"{start_time.strftime('%y%m%d%H%M%S')}_{file_par}.csv")
    ser.close()
    return data

def RunLoop(duration_acq, nLoops, file_par, threshold=200):
    print(f'Start running {nLoops} loops of {duration_acq} sec each')
    print()
    i = 1
    while i <= nLoops:
        print(f'Run now loop n. {i} of {nLoops}')
        RunIt(duration_acq=duration_acq, file_par=file_par, threshold=threshold)
        i=i+1

def ScanThreshold(duration_acq=3600, debug=False, prefix=None):
    step = 20
    for t in range(10, 255, step):
        print(f'I will now run threshold {t} (range 10-255, steps {step})')
        time.sleep(10)
        nomeFile = prefix + f'CTA-ThresholdScan_{t}'
        RunIt(duration_acq=duration_acq, file_par=nomeFile, threshold=t, debug=debug)




'''==================
     Interactive menu
=================='''
menu()
interactive()
