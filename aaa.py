
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

def menu():
    print("\n ========================= ")
    print("     WELCOME TO ArduSiPM   ")
    print(" ========================= ")
    print(" type menu() for this menu \n")
    print(" available functions are:  ")
    print("   - Info_ASPM():                Retrive basic information from ArduSiPM ")
    print("   - Acquire_ASPM():        Open connection and start acquisition")
    print("   - Save_Data():           Save recorded data on a file")
    print("   - ")
    print("   - Load_Curti_xlsx():     Load data from CVS output file")
    print("   - LoadMerge_xlsx():      Load all files from a folder")
    print("   - ")
    print("   - Plot_ADC():            1D plot of ADC spectra")

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
     Load data from file/s
=================='''
class ArduSiPM_MetaData:
    def __init__(self):
        self.FileName = 'Not-Provided'
        self.df = pd.DataFrame(columns = ['UNIXTIME', 'CPS', 'TDC', 'ADC'])

def Load_Curti_xlsx(filename=None):
    '''
    SCOPE: load data from a xlsx datafile generated from Curti acquisition program
    INPUT: the file name of the xlsx datafile
    OUTPUT: a Pandas DataFrame
    '''
    #TODO: read both the sheet of the excel file, sort the informations and return an ArduSiPM_MetaData
    if not filename:
        print("please provide a valid filename")
        return(0)
    if not filename.endswith(".xlsx"):
        print("file not .xlsx, please provide a valid filename")
        return(0)
    data_all = pd.ExcelFile(filename)
    if 'ADCTDC' in data_all.sheet_names:
        data = data_all.parse('ADCTDC')
        return(data)
    else:
        print(f'NO TDC/ADC information in file {filename}')
        return(0)

def Load_Merge_xlsx(directory=None, InName=None, OutName=None):
    '''
    SCOPE:
    INPUT: path to the folder with xlsx data files
    OUTPUT: a Pandas DataFrame
    '''
    #TODO: return an ArduSiPM_MetaData
    if not directory:
        print('PLEASE, provide a directory to scan... ')
        return(0,0)
    nFile = 0
    data = []
    slash = '/'
    if(InName): print(f"I will skip all files that does NOT contain {InName}")
    if(OutName): print(f"I will skip all files that does contain {OutName}")
    ## loops on the files of the directory
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            if InName and InName not in filename:
                print("skipping " + filename)
                continue
            if '~' in filename: continue
            if OutName and OutName in filename:
                print("skipping " + filename)
                continue
            nFile = nFile+1
            # loading and filtering data:
            print(f'loading file {directory+slash+filename}')
            data.append(Load_Curti_xlsx(directory+"/"+filename)) #this is a list of DataFraMe
    TheData = pd.concat(data, ignore_index=True) #this is a DataFrame
    return(TheData)

def Load_csv(filename=None):
    '''
    SCOPE: load data from a CSV datafile generated from the Save_Data() function
    INPUT: the file name of the csv datafile
    OUTPUT: a Pandas DataFrame
    '''
    if not filename:
        print("please provide a valid filename")
        return(0)
    if not filename.endswith(".csv"):
        print("file not .csv, please provide a valid filename")
        return(0)
    ddata = []
    with open(filename, 'r') as file:
        #rawdata = csv.reader(file, delimiter=',')
        for line in file: rawdata = line.split(',')
        for row in rawdata:
            dolpos = row.find('$')
            tpos = row.find('t')
            #vpos = row.find('v')
            ## only data with a valid time are imported
            if (dolpos <=1): continue
            CPS = row[dolpos+1]
            #print('row is '+ row)
            data = row[:dolpos]
            if not (data[0] == 't'): continue 
            if(tpos==0):
              lista=data[1:].split('t')
              for i in range(0,len(lista)):
                  vlista = lista[i].split('v')
                  TDC = vlista[0]
                  ADC = vlista[1]
                  #print(row,CPS,TDC,ADC)
                  ddata.append([0,int(CPS),int(TDC,16),int(ADC,16)])
    TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC'])
    #TheData.df = TheData.df.concat(ddata, ignore_index=True)
    #return(TheData)
    return(TheData)


'''==================
     Plotting
=================='''
def Plot_ADC(dati, binsize=16, hRange=[0,4000]):
    '''
    SCOPE: fast plot of ADC spectra
    INPUT: data
    OUTPUT: print info on screen and histo parameters
    '''
    nBin = int((hRange[1]-hRange[0])/binsize)
    title = 'ADC spectra'
    label = 'ADC channel'
    n, bins, patches = ut.Plot1D(dati.ADC, nBin=nBin, R=hRange, title=title, label=label, log=True)
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

def Search_ASPM(baudrate=115200, timeout=None):
    '''
    SCOPE: search for ArduSiPM
    NOTE: copied and adapted from the original script from V.Bocci
    INPUT: none
    OUTPUT: string with serial name
    '''
    #Scan Serial ports and found ArduSiPM
    print('Serial ports available:')
    ports = list(serial.tools.list_ports.comports())
    for i in range (0,len(ports)):
        print(ports[i])
        pippo=str(ports[i])
        if (pippo.find('Arduino')>0):
            serialport=pippo.split(" ")[0] #TODO: ? solve the com> com9 problem Francesco
            print(f"Found ArduSiPM in port {serialport}")
            return(str(serialport))
        else :
            print ("no ArduSiPM, looking more...")

def Scrivi_Seriale(comando, ser):
    if(ser):
        ser.write(comando)
        time.sleep(0.5)

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
            file.write(line.decode('ascii'))
            file.write(',')

def Acquire_ASPM(duration_acq, ser):
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
        #print(data)
        #data=data.decode('ascii')
        #print(data)
        lista.append(data)
    return(lista)

def RunIt(duration_acq=0, file_par='RawData'):
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
    Scrivi_Seriale(b's100', ser)
    Scrivi_Seriale(b'@', ser)
    print(f'Acquiring now... will stop at {stopat}')
    data = Acquire_ASPM(duration_acq, ser)
    print('SAVING DATA...')
    Save_Data(data, f"{start_time.strftime('%y%m%d%H%M%S')}_{file_par}.csv")
    ser.close()
    return data

def RunLoop(duration_acq, nLoops, file_par):
    print(f'Start running {nLoops} loops of {duration_acq} sec each')
    print()
    i = 1
    while i <= nLoops:
        print()
        print(f'Run now loop n. {i}')
        RunIt(duration_acq=duration_acq, file_par=file_par)
        i=i+1

'''==================
     Interactive menu
=================='''
menu()
interactive()
