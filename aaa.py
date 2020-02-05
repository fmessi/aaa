
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
    print("   - Load_Curti_xlsx():     Load data from xlsx output file")
    print("   - LoadMerge_xlsx():      Load all files from a folder (xlsx)")
    print("   - Load_csv():            Load data from CVS output file")
    print("   - LoadMerge_cvs():      Load all files from a folder (cvs)")
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
    print("   - Load_csv(filename=, debug=)")
    print("   - LoadMerge_cvs(directory=, InName=, OutName=, debug=)")
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

def Load_csv_old(filename=None):
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

def Load_csv(filename=None, debug=False):
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
            if not row: continue
            if debug: print(f'row is {row}')
            CPS = '-3'
            TDC = '-3'
            ADC = '-3'
            lista = '0'
            dolpos = row.find('$')
            tpos = row.find('t')
            vpos = row.find('v')
            upos = row.find('u')
            pos = (upos, tpos, vpos, dolpos)
            datastart = min(i for i in pos if i>0)
            if debug: print(f'positions are: {datastart} {pos}')
            ## only data with a valid time are imported
            if (dolpos <=1): continue
            CPS = row[dolpos+1:]
            utime = row[upos+1:datastart]
            #data = row[datastart+1:dolpos-1] ## !!! NOTA: uncomment this and comment below if Firmware is < 2.6
            data = row[datastart+1:dolpos]
            if debug: print(f'data is {data}')
            if datastart == tpos:
                lista=data.split('t')
                if debug: print(f'lista is : {lista}')
            #'''
                for i in range(0,len(lista)):
                  vlista = lista[i].split('v')
                  if vlista[0]: TDC = vlista[0]
                  if vlista[1]: ADC = vlista[1]
                  if int(ADC, 16) > 255:
                      if int(ADC[2], 16)==1:
                          print(f"    PROBLEM WITH ADC ???  file: {filename}")
                          ADC='-4' 
                  if debug: print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                  try: ddata.append([float(utime),int(CPS),int(TDC,16),int(ADC,16),int(len(lista))])
                  except:
                        print("data is corrupted")
                        print(f'row is {row}')
                        print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                        ddata.append([float(0),int(CPS),int(TDC,16),int(ADC,16),int(len(lista))])
            elif datastart == vpos:
                for i in range(0,len(data)):
                    vlista = data.split('v')
                    ## TODO
            if debug:
                TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC', 'nData'])
                return(TheData)
    TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC', 'nData'])
    #acqtime = float(TheData.UNIXTIME[len(TheData)-1]) - float(TheData.UNIXTIME[0])
    try: acqtime = pd.to_datetime(TheData.UNIXTIME[len(TheData)-1], format='%y%m%d%H%M%S.%f') - pd.to_datetime(TheData.UNIXTIME[0], format='%y%m%d%H%M%S.%f')
    except:
        print(f"    ERROR IN ACQ TIME !!! file: {filename}")
        acqtime = -3
    #TheData.df = TheData.df.concat(ddata, ignore_index=True)
    #return(TheData)
            #'''
    return(TheData, acqtime)

def Load_counts(filename=None, debug=False):
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
            if (dolpos <=1): continue
            CPS = row[dolpos+1:]
            if debug: print(f'row is {row}')
            data = row[:dolpos-1]
            if debug: print(f'data is {data}')
            utime = data[1:19]
            if debug: print(f'{utime}, {CPS}')
            TDC = '0'
            ADC = '0'
            lista = '0'
            ddata.append([float(utime),int(CPS),int(TDC,16),int(ADC,16),int(len(lista))])
    TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC', 'nData'])
    try: acqtime = pd.to_datetime(TheData.UNIXTIME[len(TheData)-1], format='%y%m%d%H%M%S.%f') - pd.to_datetime(TheData.UNIXTIME[0], format='%y%m%d%H%M%S.%f')
    except: print("    ERROR IN ACQ TIME !!!")
    return(TheData, acqtime)

def Load_Merge_csv(directory=None, InName=None, OutName=None, debug=False, SoloCounts=False):
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
    now = datetime.now()
    totACQTime = now - now
    data = []
    slash = '/'
    if(InName): print(f"I will skip all files that does NOT contain {InName}")
    if(OutName): print(f"I will skip all files that does contain {OutName}")
    ## loops on the files of the directory
    for filename in sorted(os.listdir(directory)): #, key=numericalSort):
        if filename.endswith(".csv"):
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
            #data.append(Load_csv(directory+"/"+filename)) #this is a list of DataFraMe
            if not (SoloCounts): ldata, time = (Load_csv(directory+"/"+filename))
            if (SoloCounts): ldata, time = Load_counts(directory+"/"+filename)
            data.append(ldata) #this is a list of DataFraMe
            try: totACQTime = totACQTime + time
            except: print("    ERROR IN ACQ TIME !!! file: {filename}")
            if debug: print(f'Total acquisition: {totACQTime.total_seconds()} sec. last file time: {time.total_seconds()} sec.')
    TheData = pd.concat(data, ignore_index=True) #this is a DataFrame
    print(f'{nFile} files loaded for {totACQTime.total_seconds()} seconds of acquiring time')
    return(TheData, totACQTime)

'''==================
     Plotting
=================='''
def Plot_ADC(dati, binsize=16, hRange=[0,4095], label='no_label', weights=None, log=True, ylabel=None, fig=1):
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
        ser.write(b'm')
        time.sleep(2)
        ser.write(comando)
        time.sleep(2)
        ser.write(b'e')
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
     Data analysis
=================='''

def DataQuality(data, label=None, fig=1):
    gen = data.CPS-data.nData
    w = [1/len(gen)] * len(gen)
    #FigSize = [11.69,8.27] #A4 = 8.27x11.69inch
    #plt.figure(fig, FigSize)
    #plt.title('CPS - ndata')
    n, bins, patches = ut.Plot1D(gen, nBin=max(gen), R=(0,max(gen)+1), label=label, weights=w, xlabel='CPS-nData', title='expected_counts - recorded_counts', c=fig)
    plt.ylabel('%')
    return(n, bins, patches)

def Anal(directory='.', check=False, SoloCounts=False):
    bg, t_bg = Load_Merge_csv(directory, InName = 'bg', OutName='SoloCounts')
    w_bg = [1/t_bg.total_seconds()] * len(bg.ADC)

    therm, t_therm = Load_Merge_csv(directory, InName = 'thermal', OutName='SoloCounts')
    w_therm = [1/t_therm.total_seconds()] * len(therm.ADC)

    #fast, t_fast = Load_Merge_csv(directory, InName = 'fast', OutName='fast2', SoloCounts=SoloCounts)
    #w_fast = [1/t_fast.total_seconds()] * len(fast.ADC)

    fast2, t_fast2 = Load_Merge_csv(directory, InName = 'fast2', OutName='SoloCounts')
    w_fast2 = [1/t_fast2.total_seconds()] * len(fast2.ADC)

    Co60, t_Co60 = Load_Merge_csv(directory, InName = 'Co60', OutName='SoloCounts')
    w_Co60 = [1/t_Co60.total_seconds()] * len(Co60.ADC)

    Plot_ADC(bg, label='bg', weights=w_bg, ylabel='rate', fig=1) #, log=False)
    Plot_ADC(therm, label='therm', weights=w_therm, fig=1) #, log=False)
    #Plot_ADC(fast, label='fast', weights=w_fast, fig=1)
    Plot_ADC(Co60, label='gamma (Co-60)', weights=w_Co60, fig=1)
    plt.ylabel('rate (counts/sec)')
    plt.legend()

    Plot_CPS(bg, label='bg', fig=3)
    Plot_CPS(therm, label='therm', fig=3)
    #Plot_CPS(fast, label='fast', fig=3)
    Plot_CPS(fast2, label='fast2', fig=3)
    Plot_CPS(Co60, label='gamma (Co-60)', fig=3)
    #plt.ylabel('rate (counts/sec)')
    plt.legend()

    if check:
        DataQuality(bg, label='bg',fig=2)
        DataQuality(therm, label='thermal',fig=2)
        DataQuality(fast2, label='fast2',fig=2)
        DataQuality(Co60, label='Co60',fig=2)
        plt.legend()

def ThresholdScan(directory='.', OutName=None):
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".csv"): continue
        if OutName and OutName in filename: continue
        #print(f'loading file {directory}/{filename}')
        threshold = filename.split('Scan_')[1].split('.')[0]
        #print(filename, threshold)
        ldata, time = Load_csv(directory+"/"+filename)
        answer = ldata.query('ADC > 16')
        Plot_ADC(answer, label=f'threshold {threshold}',fig=1)
        Plot_CPS(ldata, label=f'threshold {threshold}',fig=2)

'''==================
     Interactive menu
=================='''
menu()
interactive()
