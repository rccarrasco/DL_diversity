#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 15:25:36 2021

@author: UA - DLIS - RCC

Predict asympotic value for the diversity index of sample books
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from div import Text, BestFit
import configparser
import zipfile
    
"""
  Main code
"""
if __name__ == '__main__':
    # plot settings
    config = configparser.ConfigParser()
    config.read('diversity.ini')
    if len(sys.argv) > 1:
        archive_name = sys.argv[1]
    else:
        archive_name  = config.get('LEXICAL', 'archive_name')
    interval_size = 4000
    step = 1000 # finer granularity for predictions
    
    # main loop
    fig, subplot = plt.subplots(3, 1, sharey=True, figsize=(6, 10))
    archive = zipfile.ZipFile(archive_name, 'r')
    for n, filename in enumerate(archive.namelist()):
        content = archive.open(filename).read().decode('UTF-8')
        text = Text(content)
        stats = text.token_diversity(step)
        X = np.array(list(stats.keys()))
        Y = np.array(list(stats.values()))
        label = os.path.basename(filename).split('.')[0]
        subplot[n].plot(X[::4], Y[::4], '.', markersize=8)
        short_name = os.path.basename(filename).split('.')[0].replace('_', ' ')
        print(short_name, 
              len(text), 'tokens; ',
              text.dict_size(), 'types;')
       
        # use initial 10000 tokens to predict the shape of the curve
        XX = X[:10]
        YY = Y[:10]
        # exponential fit
        bf = BestFit('exp2')
        pars = bf.fit(XX, YY, p0=(1000, 1000))
        par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
        subplot[n].plot(X, bf.f(X, *pars), '.', label='M1')
        print('M1 pars=', par_text)
        
        # quotient fit
        bf = BestFit('bio_model2')
        pars = bf.fit(XX, YY, p0=(1000, 1000))
        par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
        subplot[n].plot(X, bf.f(X, *pars), '+', label='M2')
        print('M2 pars=', par_text)
        
         # Power fit
        bf = BestFit('bio_model3')
        pars = bf.fit(XX, YY, p0=(1000, 1, 10))
        par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
        subplot[n].plot(X, bf.f(X, *pars), '-', label='M3')
        print('M3 pars=', par_text)
        
        # Power fit
        bf = BestFit('power')
        pars = bf.fit(X, Y, p0=(1000, 1, 10), 
                      bounds=([100, 0., 1], [2000, 10, 40000]))
        par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
        subplot[n].plot(X, bf.f(X, *pars), '--', label='M4')
        print('M4 pars=', par_text)
       
        _, xhigh = plt.xlim()
        xrange = list(range(0, int(xhigh), 20000))
        plt.xticks(xrange,  [x // 1000 for x in xrange])
        if xhigh > 140000:
            subplot[n].set_xlim(0, 140000)
        subplot[n].grid()
        subplot[n].set_title(short_name)
        
    fig.supxlabel('thousands of words')
    fig.supylabel('Shannon diversity index')      
    fig.suptitle('Diversity of tokens')
    plt.legend(loc='upper left')
    plt.tight_layout()
    output = 'plots/model_prediction.png'
    plt.savefig(output, dpi=300)
    print('Saved to', output)