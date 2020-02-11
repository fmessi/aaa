#!/usr/bin/env python3

'''
 --------------------------------------------------------------------
|              aaa - ArduSiPM Acquisition & Analysis                 |
 --------------------------------------------------------------------
| Python libraries for the ArduSiPM  =  data analysis                |
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
import numpy as np
import pandas as pd
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import Utility as ut
import a_load as lf
import a_plots as plot

'''==================
     Data analysis
=================='''

def DataQuality(data, label=None, fig=1):
    m = max(data.CPS)
    #r = ((-0.5,m+0.5),(0,100))
    #b = (m+1, 100)
    r = ((0.5,m+0.5),(0,100))
    b = (m, 100)
    plt.figure(fig)
    nzero = 0
    for counts in set(data.CPS):
        ans = data.query(f'CPS=={counts}')
        if not counts==0:
            persi = (ans.CPS-ans.nData)/ans.CPS*100
        else:
            persi = np.zeros(shape=(1,len(ans.CPS)))
        try: h = plt.hist2d(ans.CPS,persi, bins=b, range=r, cmin=1)#, density=True)
        except:
            print(counts)
            #plt.show()
            #input("Press Enter to continue...")
    plt.xlabel('CPS')
    plt.ylabel('number of ADC loss ($-#ADC)')
    plt.colorbar()
    return(h)

def BC408(directory='.', check=False, SoloCounts=False):
    bg, t_bg = lf.Load_Merge_csv(directory, InName = 'bg')
    w_bg = [1/t_bg.total_seconds()] * len(bg.ADC)

    therm, t_therm = lf.Load_Merge_csv(directory, InName = 'therm-TAC-100mV')
    w_therm = [1/t_therm.total_seconds()] * len(therm.ADC)

    fast, t_fast = lf.Load_Merge_csv(directory, InName = 'fast')
    w_fast = [1/t_fast.total_seconds()] * len(fast.ADC)

    #Co60, t_Co60 = lf.Load_Merge_csv(directory, InName = 'Co60', OutName='SoloCounts')
    #w_Co60 = [1/t_Co60.total_seconds()] * len(Co60.ADC)

    plot.Plot_ADC(bg, label='bg', weights=w_bg, ylabel='rate', fig=1) #, log=False)
    plot.Plot_ADC(therm, label='therm', weights=w_therm, fig=1) #, log=False)
    plot.Plot_ADC(fast, label='fast', weights=w_fast, fig=1)
    #plot.Plot_ADC(Co60, label='gamma (Co-60)', weights=w_Co60, fig=1)
    plt.ylabel('rate (counts/sec)')
    plt.legend()

    plot.Plot_CPS(bg, label='bg', fig=2)
    plot.Plot_CPS(therm, label='therm', fig=2)
    plot.Plot_CPS(fast, label='fast', fig=2)
    #plot.Plot_CPS(Co60, label='gamma (Co-60)', fig=2)
    #plt.ylabel('rate (counts/sec)')
    plt.legend()

    if check:
        DataQuality(bg, label='bg',fig=3)
        DataQuality(therm, label='thermal',fig=3)
        DataQuality(fast, label='fast',fig=3)
        DataQuality(Co60, label='Co60',fig=3)
        plt.legend()

def GS20(directory='.', check=False, SoloCounts=False):
    bg, t_bg = lf.Load_Merge_csv(directory, InName = 'bg')
    w_bg = [1/t_bg.total_seconds()] * len(bg.ADC)

    therm, t_therm = lf.Load_Merge_csv(directory, InName = 'therm')
    w_therm = [1/t_therm.total_seconds()] * len(therm.ADC)

    fast, t_fast = lf.Load_Merge_csv(directory, InName = 'fast')
    w_fast = [1/t_fast.total_seconds()] * len(fast.ADC)

    #Co60, t_Co60 = Load_Merge_csv(directory, InName = 'Co60', OutName='SoloCounts')
    #w_Co60 = [1/t_Co60.total_seconds()] * len(Co60.ADC)

    plot.Plot_ADC(bg, label='bg', weights=w_bg, ylabel='rate', fig=1) #, log=False)
    plot.Plot_ADC(therm, label='therm', weights=w_therm, fig=1) #, log=False)
    plot.Plot_ADC(fast, label='fast', weights=w_fast, fig=1)
    #plot.Plot_ADC(Co60, label='gamma (Co-60)', weights=w_Co60, fig=1)
    plt.ylabel('rate (counts/sec)')
    plt.legend()

    plot.Plot_CPS(bg, label='bg', fig=2)
    plot.Plot_CPS(therm, label='therm', fig=2)
    plot.Plot_CPS(fast, label='fast', fig=2)
    #plot.Plot_CPS(Co60, label='gamma (Co-60)', fig=2)
    #plt.ylabel('rate (counts/sec)')
    plt.legend()

    if check:
        DataQuality(bg, label='bg',fig=3)
        DataQuality(therm, label='thermal',fig=3)
        DataQuality(fast, label='fast',fig=3)
        #DataQuality(Co60, label='Co60',fig=3)
        plt.legend()

def ThresholdScan(directory='.', OutName=None):
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".csv"): continue
        if OutName and OutName in filename: continue
        #print(f'loading file {directory}/{filename}')
        threshold = filename.split('Scan_')[1].split('.')[0]
        #print(filename, threshold)
        ldata, time = lf.Load_csv(directory+"/"+filename)
        answer = ldata.query('ADC > 16')
        Plot_ADC(answer, label=f'threshold {threshold}',fig=1)
        Plot_CPS(ldata, label=f'threshold {threshold}',fig=2)
