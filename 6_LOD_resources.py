#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:06:48 2021

@author: rafa
"""
import os
import re
from math import log
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
    
input_dir = 'input/LOD'

res = pd.DataFrame()
for filename in os.listdir(f'{input_dir}'):
    m = re.match('(\w+)-(\w+).txt', filename)
    host = m.group(1).upper()
    resource_type = m.group(2)
    if resource_type in ('class', 'property'):
        path = os.path.join(input_dir, filename)
        df = pd.read_csv(path, sep=' ', header=None)
        c = Counter(dict(zip(df[0], df[1])))
        freqs = df[1].astype(int)
        total = sum(freqs)
        entropy = log(total, 2) - sum(f * log(f, 2) for f in freqs) / total 
        diversity = 2 ** entropy
        rate = diversity / len(df)
        row = {  
            'resource type': resource_type, 
            'richness':len(df),
            'diversity':diversity,   
            'rate':rate
            }
        res = res.append(pd.Series(row, name=host))        

pivot = res.pivot_table(index=res.index, columns='resource type', 
                        values=('richness', 'diversity', 'rate'))
pivot = pivot.swaplevel(0,1, axis=1).sort_index(axis=1) 
print(pivot)
pivot.to_excel('output/LOD_resources.xlsx')

plt.clf()
X, Y = pivot['class', 'diversity'], pivot['property', 'diversity']
plt.plot(X, Y, 'o')
plt.xlim(1, 15)
plt.ylim(5, 65)
plt.title('Diversity of linked open data collections')
plt.xlabel('diversity of classes')
plt.ylabel('diversity of properties')
for host, x, y in zip(pivot.index, X, Y):
    plt.annotate(host, (x + 0.1, y + 1))
plt.grid()
plt.savefig('plots/LOD_resources.png', dpi=300)