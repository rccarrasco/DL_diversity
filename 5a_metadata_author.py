#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 11:00:29 2021

@author: UA - DLSI - RCC
"""
import configparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from div import richness, shannon_diversty_index, dr_rate

def average_number_occurrences(items):
    """
    Parameters
    ----------
    items : iterable
        An itrerable collection of repeatable items.

    Returns
    -------
    float
        average number of occurences of unique items.

    """
    values = Counter(items).values()
    
    return sum(values) / len(values)

# 
def plot_author_diversity(host, df, years):
    """
    Create cummulative plot for the specified data, range of years 

    Parameters
    ----------
    host : str
        Host institution short name, to be used in the plot title.
    df : DataFrame
        DataFrame with columns YEAR and MAIN_AUTHOR.
    years : iterable collection of int
        The years to be used as X-points for the plot
    """
    plt.clf()
    X = np.array(years)
    R = list()  # richness
    D = list()  # diversity
    for year in X:
        selection = df[df.YEAR <= year]
        R.append(richness(selection.MAIN_AUTHOR))
        D.append(shannon_diversty_index(selection.MAIN_AUTHOR))
    
    plt.plot(X, R, 's', label='richness')
    plt.plot(X, D, 'o', label='diversity')
   
    plt.legend(loc='upper left')
    plt.grid()
    xticks = [x for x in range(min(X), max(X) + 1) if x % 5 == 0]
    plt.xticks(xticks, xticks)
    _, yhigh = plt.ylim()
    plt.ylim(0, 1.1 * yhigh)
    plt.title(f'Authors in the catalogue ({host})')
    plt.savefig(f'plots/authors_{host}.png', dpi=300)
    

# Main code
config = configparser.ConfigParser()
config.read('diversity.ini')
params = config['METADATA']
hosts = params['hosts'].split()
filenames = params['FILENAMES'].split()
intervals = params['INTERVALS'].split()

for host, filename, interval in zip(hosts, filenames, intervals):
    print('Processing', host)
    df = pd.read_csv(filename, sep='\t').fillna('')
    df = df[(df.YEAR!='')&(df.MAIN_AUTHOR!='')]
    first, last = map(int, interval.split('-'))
    plot_author_diversity(host, df, range(first, last + 1))
    print('DR_rate=', dr_rate(df.MAIN_AUTHOR))
    print('AV NUM TITLES=', average_number_occurrences(df.MAIN_AUTHOR))
