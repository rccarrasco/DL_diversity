#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 10:27:26 2021

@author: UA - DLSI - RCC

Create plots of vocabulary size for three sample books
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from div import Text, BestFit
import configparser
import zipfile


def load_params():
    """
    Load configuration file
    Returns
    -------
    dict
        plot parameters.
    """
    config = configparser.ConfigParser()
    config.read('diversity.ini')
    
    return config['LEXICAL']

if __name__ == '__main__':
    # plot settings
    params = load_params()
    if len(sys.argv) > 1:
        archive_name = sys.argv[1]
    else:
        archive_name  = params.get('archive_name')
    markers = tuple(map(str.strip, params.get('markers').split(',')))
    markersize = int(params.get('markersize')) 
    interval_size = int(params.get('intervalsize')) 
    
    # main loop
    archive = zipfile.ZipFile(archive_name, 'r')
    for n, filename in enumerate(archive.namelist()):
        content = archive.open(filename).read().decode('UTF-8')
        text = Text(content)
        stats = text.dict_size(interval_size)
        X = np.array(list(stats.keys()))
        Y = np.array(list(stats.values()))
        label = os.path.basename(filename).split('.')[0].replace('_', ' ')
        marker = markers[n % len(markers)]
        fig = plt.plot(X, Y, marker, markersize=markersize, label = label)[0]
        color = fig.get_color()
        bf = BestFit('simple_power')
        pars = bf.fit(X, Y)
        par_text = ', '.join(map(lambda x: f'{x:.2f}', pars))
        print(label, par_text)
        plt.plot(X, bf.f(X, *pars), '--', linewidth=0.5, color=color)
        
    _, xhigh = plt.xlim()
    xrange = list(range(0, int(xhigh), 20000))    
    plt.xticks(xrange,  [x // 1000 for x in xrange])
    plt.xlabel('thousands of tokens')
    plt.ylabel('thousands of types')  
    plt.title('Vocabulary size')
    plt.grid()
    plt.legend(loc='upper left', markerscale=2)
    plt.tight_layout()
    plt.savefig('plots/vocabulary_size.png', dpi=300)
   
