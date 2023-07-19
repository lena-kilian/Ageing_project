#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import copy as cp
import seaborn as sns
import matplotlib.pyplot as plt

# set working directory
# make different path depending on operating system

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

results = pd.read_excel(output_path + 'outputs/GHG_by_hhd_types.xlsx', sheet_name=None)

# aggregate to Coicop 2
new_cols = results[list(results.keys())[0]].loc[:,'1.1.1 Bread and cereals':].columns.tolist()
new_cols = dict(zip(new_cols, [x.split('.')[0] for x in new_cols])) # [x.split('.')[0] + '.' + x.replace(' ', '.').split('.')[1] for x in new_cols]

aggregated = pd.DataFrame()
for hhd_type in list(results.keys()):
    temp = results[hhd_type].rename(columns=new_cols).sum(axis=1, level=0)
    
    for year in temp[['year']].drop_duplicates()['year'].tolist():
        temp2 = temp.loc[(temp['year'] == year) & (temp['count'] > 20)]
        temp2['hhd'] = temp2['hhd_type'] + '__' + temp['hhd_sex_composition'] + '__' + temp['year'].astype(str)
        temp2 = temp2.drop(['Unnamed: 0', 'hhd_type', 'hhd_sex_composition', 'year'], axis=1)\
            .set_index(['group', 'hhd', 'count', 'weight', 'no_people', 'OECD scale']).stack().reset_index()\
                .rename(columns={'level_6':'CCP2', 0:'GHG'})
        
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,5))
        sns.barplot(ax=ax, data=temp2, x='CCP2', y='GHG', hue='hhd')
        plt.xticks(rotation=90)
        plt.show()
