#!/usr/bin/env python3

'''
 --------------------------------------------------------------------
|                         Python utilities                           |
 --------------------------------------------------------------------
| Python simple functions                                            |
|                                                                    |
| history:                                                           |
| 200211 - F.Messi - file created from old aaa.py                    |
|                                                                    |
 --------------------------------------------------------------------
'''

import matplotlib.pyplot as plt
import Utility as ut


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
