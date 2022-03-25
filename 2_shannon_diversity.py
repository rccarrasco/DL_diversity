#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 10:27:26 2021

@author: UA - DLSI - RCC

Compute Shannon diversity index for sample books
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
    archive = zipfile.ZipFile(archive_name, 'r')
    for n, filename in enumerate(archive.namelist()):
        content = archive.open(filename).read().decode('UTF-8')
        text = Text(content) 
        stats = text.token_diversity(interval_size)
        X = np.array(list(stats.keys()))
        Y = np.array(list(stats.values()))
        label = os.path.basename(filename).split('.')[0].replace('_', ' ')
        marker = markers[n % len(markers)] #+ '--'
        plt.plot(X, Y, marker, markersize=markersize, label=label)
        bf = BestFit('bio_model2')
        pars = bf.fit(X, Y, p0=(1000, 10000))
        par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
        print(label, par_text)
        
    _, xhigh = plt.xlim()
    xrange = list(range(0, int(xhigh), 20000))    
    plt.xticks(xrange,  [x // 1000 for x in xrange])
    plt.xlabel('thousands of words')
    plt.ylabel('Shannon diversity index')  
    plt.title('Diversity of tokens')
    plt.grid()
    plt.legend(loc='lower right', markerscale=2)
    plt.tight_layout()
    plt.savefig('plots/shannon_diversity.png', dpi=300)
