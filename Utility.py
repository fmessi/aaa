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

def Plot1D(dataArray, nBin=0, R=(0,0), title='title here...', label='here label...', c=1, log=False):
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
    plt.xlabel(label)
    #dataArray.hist(bins=nBin, histtype='step', fill=False)
    n, bins, patches = plt.hist(dataArray, bins=nBin, range=R,  histtype='step', fill=False, log=log)
    #return dataArray.hist(bins=nBin, histtype='step', fill=False ) #,edgecolor='black')
    return n, bins, patches
