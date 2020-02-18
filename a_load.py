#!/usr/bin/env python3

'''
 --------------------------------------------------------------------
|              aaa - ArduSiPM Acquisition & Analysis                 |
 --------------------------------------------------------------------
| Python libraries for the ArduSiPM  =  load data from files         |
| project web: https://sites.google.com/view/particle-detectors/home |
| code repository: https://github.com/fmessi/aaa.git                 |
|                                                                    |
| history:                                                           |
| 200211 - F.Messi - file created from old aaa.py                    |
 --------------------------------------------------------------------
'''

import sys
import os
import time
from datetime import datetime, timedelta
import csv
import pandas as pd

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
            if debug:
                print('')
                print(f'row is {row}')
            CPS = '-3'
            TDC = '-3'
            ADC = '-3'
            lista = '0'
            QF = 0 ## Quality factor, if zero --> data are perfect as expected
            dolpos = row.find('$')
            tpos = row.find('t')
            vpos = row.find('v')
            upos = row.find('u')
            pos = (upos, tpos, vpos, dolpos)
            datastart = min(i for i in pos if i>0)
            if debug: print(f'positions are: {datastart} {pos}')
            ## only data with a valid time are imported
            if (dolpos <=1):
                QF = QF +1
                ddata.append([float(0),int(CPS),int(TDC,16),int(ADC,16),int(0),int(QF)])
                continue
            CPS = row[dolpos+1:]
            utime = row[upos+1:datastart]
            #data = row[datastart+1:dolpos-1] ## !!! NOTA: uncomment this and comment below if Firmware is < 2.6
            data = row[datastart+1:dolpos]
            if debug: print(f'data is {data}')
            if tpos>0 and vpos < tpos:
                QF = QF +1
                if debug: print(f"data is corrupted. Row is: {row}, {filename}")
                try:
                    if debug: print(f'scrivo: [{float(utime)},{int(CPS)},{int(TDC,16)},{int(ADC,16)},{int(len(lista))}]')
                    ADC = '-5'
                    ddata.append([float(utime),int(CPS),int(TDC,16),int(ADC,16),int(len(lista)),int(QF)])
                except:
                        print("data is corrupted")
                        print(f'row is {row}')
                        print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                        ddata.append([float(0),int(CPS),int(TDC,16),int(ADC,16),int(len(lista)),int(QF)])
                continue
            if datastart == dolpos:
                try:
                    if debug: print(f'scrivo: [{float(utime)},{int(CPS)},{int(TDC,16)},{int(ADC,16)},{int(0)}]')
                    ddata.append([float(utime),int(CPS),int(TDC,16),int(ADC,16),int(0),int(QF)])
                except:
                    QF = QF +1
                    print("data is corrupted")
                    print(f'row is {row}')
                    print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                    ddata.append([float(0),int(CPS),int(TDC,16),int(ADC,16),int(len(lista)),int(QF)])
            elif datastart == tpos:
                lista=data.split('t')
                #if debug: print(f'lista is : {lista}')
            #'''
                for i in range(0,len(lista)):
                  vlista = lista[i].split('v')
                  if vlista[0]: TDC = vlista[0]
                  if vlista[1]: ADC = vlista[1]
                  if int(ADC, 16) > 255:
                      if int(ADC[2], 16)==1:
                          print(f"    PROBLEM WITH ADC ???  file: {filename}")
                          ADC='-4'
                  #if debug: print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                  try:
                    if debug: print(f'scrivo: [{float(utime)},{int(CPS)},{int(TDC,16)},{int(ADC,16)},{int(len(lista))}]')
                    ddata.append([float(utime),int(CPS),int(TDC,16),int(ADC,16),int(len(lista)),int(QF)])
                  except:
                        QF = QF + 1
                        print("data is corrupted")
                        print(f'row is {row}')
                        print(f'{utime}, {CPS}, {TDC}, {ADC}, {len(lista)}')
                        ddata.append([float(0),int(CPS),int(TDC,16),int(ADC,16),int(len(lista)),int(QF)])
            elif datastart == vpos:
                for i in range(0,len(data)):
                    vlista = data.split('v')
                    ## TODO
            #if debug:
            #    TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC', 'nData'])
            #    return(TheData)
    TheData = pd.DataFrame(ddata, columns=['UNIXTIME', 'CPS', 'TDC', 'ADC', 'nData', 'QF'])
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
