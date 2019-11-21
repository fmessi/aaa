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
    print("   - info():                Retrive basic information from ArduSiPM ")
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
def info():
    '''
    SCOPE: call to the original info script from V.Bocci
    INPUT: none
    OUTPUT: print info on screen
    '''
    sys.path.append('Valerio/')
    import ArduSiPM_info.py

menu()
interactive()