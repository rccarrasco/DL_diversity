#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 10:27:26 2021

@author: UA - DLSI - RCC

Compute diversity for a sample of books and 
present it in a plot as a function of the text length 
"""
import sys, os
import configparser
import numpy as np
import matplotlib.pyplot as plt
from div import Text, BestFit
import zipfile
def load_params():
    """
    Load configuration file
    Returns
    -------
    dict
        plot parameters.
    """
   
    
    return config['LEXICAL']
if __name__ == '__main__':
    if len(sys.argv) > 1:
        archive_name = sys.argv[1]
    else:
         config = configparser.ConfigParser()
         config.read('diversity.ini')
         archive_name  = config.get('AUTHOR', 'archive_name')
    
    archive = zipfile.ZipFile(archive_name, 'r')
                
    res = list()
    for filename in archive.namelist():
        content = archive.open(filename).read().decode('UTF-8')
        text = Text(content)
        stats = text.token_diversity(1000)
        X = np.array(list(stats.keys()))
        Y = np.array(list(stats.values()))
        bf = BestFit('power')
        p0 = (1000, 1, 10)
        bounds = ([100, 0., 1], [2000, 10, 80000])
        try:
            pars = bf.fit(X, Y, p0=p0, bounds=bounds)
            par_text = ', '.join(map(lambda x: f'{x:.1f}', pars))
            print(filename, len(text), '\n\t', par_text)
            res.append((len(text), pars[0]))
        except RuntimeError:
            print(filename, len(text), 'best fit not found\n')
       
    
    X, Y = zip(*res)
    plt.plot(X, Y, 'o')
    print(f"Pearson's correlation = {np.corrcoef(X, Y)[0,1]:.2f}")
    plt.xlabel('thousands of words')
    plt.ylabel('Shannon diversity index')  
    plt.grid() 
    plt.tight_layout()
    basename = '.'.join(os.path.basename(archive_name).split('.')[:-1])
    plt.savefig(f'plots/{basename}.png', dpi=300)
   