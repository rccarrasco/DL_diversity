#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 11:00:29 2021

@author: UA - DLSI - RCC
"""
import configparser
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from div import richness, shannon_diversty_index, dr_rate


def plot_subject_diversity(host, df, column_name, years, r_scale=1):
    """
    Create cummulative plot for the specified data, range of years 
    Parameters
    ----------
    host : str
        Host institution short name, to be used in the plot title.
    df : DataFrame
        DataFrame with columns YEAR and column_name.
    years : iterable collection of int
        The years to be used as X-points for the plot
    r_scale : int, optional
        Scale for the reduction of richness. The default is 1.
    """
    plt.clf()
    X = np.array(years)
    R = list()  # richness
    D = list()  # diversity
    for year in X:
        values = df[df.YEAR <= year][column_name]
        R.append(richness(values) / r_scale)
        D.append(shannon_diversty_index(values))
    if r_scale == 1:
        plt.plot(X, R, 's', label='richness')
    else: 
        plt.plot(X, R, 's', label=f'richness / {r_scale}')
    plt.plot(X, D, 'o', label='diversity')
    
    plt.legend(loc='upper left')
    plt.grid()
    xticks = [x for x in range(min(X), max(X) + 1) if x % 5 == 0]
    plt.xticks(xticks, xticks)
    _, yhigh = plt.ylim()
    plt.ylim(0, 1.1 * yhigh)
    name =  column_name.lower().replace('_', ' ')
    plt.title(f'Diversity of {name} ({host})')
    plt.savefig(f'plots/{column_name}_{host}.png', dpi=300)
    
   


def split_subject(subject):
    """
    

    Parameters
    ----------
    subject : str
        Complete subject descriptor, such as Commerce--History
    Returns
    -------
    list of str
    Subdivisions (at least two characters long) in one subject, for example, 
    ['Commerce', 'History'].
    """
    tokens = re.split('\s*--\s*', subject.strip())

    return list(filter(lambda t: len(t) > 1 , map(str.strip, tokens)))
  

def split(s, separator):
    """
    Return all  tokens in the string after split by symbol s    

    Parameters
    ----------
    s : str
        input string.
    separator : str
        character used as separator.

    Returns
    -------
    list
        All tokens of length at least 2 after splitting s by separators.

    """
    tokens = re.split('\s*' + separator + '\s*', s.strip())
    
    return list(filter(lambda t: len(t) > 1 , map(str.strip, tokens)))

#----------------------------------------------------  
# Main code
config = configparser.ConfigParser()
config.read('diversity.ini')
params = config['METADATA']
hosts = params['hosts'].split()
filenames = params['FILENAMES'].split()
intervals = params['INTERVALS'].split()
scale =  map(int, params['RICHNESS_SCALES'].split())

for host, filename, interval in zip(hosts, filenames, intervals):
    print('Processing', host)
    first, last = map(int, interval.split('-'))
    df = pd.read_csv(filename, sep='\t').fillna('')
    df = df[(df.YEAR!='')&(df.SUBJECT_HEADINGS.str.len() > 1)]
    df['SUBJECT_HEADINGS'] = df.SUBJECT_HEADINGS.apply(lambda s: split(s, '@'))
    df = df.explode('SUBJECT_HEADINGS')
    plot_subject_diversity(host, 
                           df, 
                           'SUBJECT_HEADINGS', 
                           range(first, last + 1),  
                           next(scale))

    print('DR_RATE=', dr_rate(df.SUBJECT_HEADINGS))
    df['SH_SUBFIELDS'] = df['SUBJECT_HEADINHS'].map(split_subject)
    dfe = df.explode('SH_SUBFIELDS')
    plot_subject_diversity(host, 
                           dfe,
                           'SH_SUBFIELDS', 
                           range(first, last + 1), 
                           next(scale))

    