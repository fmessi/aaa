#!/usr/bin/env python3

'''
 --------------------------------------------------------------------
|                         Python utilities                           |
 --------------------------------------------------------------------
| Python simple functions                                            |
|                                                                    |
| history:                                                           |
| 191120 - F.Messi - Plot1D() from AMBA project                      |
|                                                                    |
 --------------------------------------------------------------------
'''

import matplotlib.pyplot as plt
import numpy as np

def Plot1D(dataArray, nBin=0, R=(0,0), title='title here...', xlabel='here label...', label='data', c=1, log=False, weights=None):
    '''
    SCOPE: a 1D histo function...
    INPUT:
    OUTPUT:
    '''
    if nBin==0 :
        nBin = (int(max(dataArray)))
    if R==(0,0):
        R = (dataArray.min()-0.5, dataArray.max()+0.5)
    FigSize = [11.69,8.27] #A4 = 8.27x11.69inch
    fig = plt.figure(c,FigSize)
    plt.title(title)
    plt.xlabel(xlabel)
    #dataArray.hist(bins=nBin, histtype='step', fill=False)
    n, bins, patches = plt.hist(dataArray, bins=nBin, range=R,  histtype='step', fill=False, log=log, label=label, weights=weights)
    #return dataArray.hist(bins=nBin, histtype='step', fill=False ) #,edgecolor='black')
    return n, bins, patches

def IrradiationRate(A = 2500, D = 1500, R = 2.99E6):
    '''
    calculate the irradiation rate from the setup
    '''
    #A = 2500 ## active area of the detector (in mmˆ2)
    #D = 1500 ## distance from the source (in mm)
    #R = 2.99E6  ## emission rate of the source (in n/sec)
    ## PuBe => R = 2.99E6 n/sec  // D = 130+acquarium
    ## AmBe => R = 1.14E6 n/sec  // D = 255 mm
    ## Co60 => R =   // D = 110 mm
    sigma = A / (4 * np.pi * D * D) * R
    return(sigma)

def CalculateIrradiation(A = 2500, D = 1500, Rmin=100, Rmax=2500,
                         R = 2.99E6, label='source'):
    Ir = []
    d = []
    for a in range(Rmin,Rmax):
        Ir.append(IrradiationRate(A=A, D=a, R=R))
        d.append(a)
    plt.plot(d,Ir, label=label)
    plt.xlabel('distance (mm)')
    plt.ylabel('irradiation (n/sec)')
    plt.legend()
