#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# set working directory
# make different path depending on operating system

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

results = pd.read_excel(output_path + 'outputs/GHG_by_hhds.xlsx', sheet_name=None, index_col='case')

# aggregate to Coicop 1 or 2
new_cols = results[list(results.keys())[0]].loc[:,'1.1.1 Bread and cereals':].columns.tolist()
new_cols = dict(zip(new_cols, [x.split('.')[0] for x in new_cols])) # [x.split('.')[0] + '.' + x.replace(' ', '.').split('.')[1] for x in new_cols]

cats = []
for item in new_cols.values():
    if item not in cats:
        cats.append(item)

aggregated = pd.DataFrame()
for year in list(results.keys()):
    temp = results[year].rename(columns=new_cols).sum(axis=1, level=0)\
        .set_index(['household_comp', 'age_group', 'gender', 'dwelling_type'])
    temp['pop'] = temp['weight'] * temp['no_people']
    
    temp[cats + ['rooms_per_person', '']] = temp[cats + ['rooms_per_person']].apply(lambda x: x*temp['pop'])
    temp['count'] = 1
    temp = temp.sum(axis=0, level=['household_comp', 'age_group', 'gender', 'dwelling_type'])\
        [['pop', 'rooms_per_person', 'count'] + cats]
    temp[cats + ['rooms_per_person']] = temp[cats + ['rooms_per_person']].apply(lambda x: x/temp['pop'])
    
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,5))
    sns.barplot(ax=ax, data=temp, x='CCP2', y='GHG', hue='hhd')
    plt.xticks(rotation=90)
    plt.show()
