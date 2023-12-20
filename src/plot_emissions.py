#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import copy as cp

# set working directory
# make different path depending on operating system

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

results = pd.read_excel(output_path + 'outputs/CO2_by_hhds.xlsx', sheet_name=None, index_col='case')

years = list(results.keys())
# keep only categories linked to fuel burning in home; electricity; personal travel
results_agg = pd.DataFrame()
for year in years:
    temp = cp.copy(results[year])
    temp['pop'] = temp['no_people'] * temp['weight']
    print(year, temp['weight'].mean(), temp['pop'].sum())
    temp['total'] = temp.loc[:,'1.1.1 Bread and cereals':'12.7.1 Other services n.e.c.'].sum(1)
    cats = temp.loc[:,'7.1 1 Motor cars':'7.3.4 Other transport services'].columns.tolist() + ['total']
    temp = temp[cats + ['pop', 'weight']]
    
    temp[cats] = temp[cats].apply(lambda x:x*temp['weight'])
    temp = pd.DataFrame(temp.sum()).T
    
    temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])
    
    temp['year'] = int(year)
    results_agg = results_agg.append(temp)


cat_dict = {'4.5.1 Electricity':'Electricity', '4.5.2 Gas':'Gas', 
            '4.5.3 Liquid fuels':'Other home energy', '4.5.4 Solid fuels':'Other home energy', '4.5.5 Heat energy':'Other home energy',  
            '7.2.2 Fuels and lubricants for personal transport equipment':'Personal transport fuel'}

cats = []
for item in list(cat_dict.values()):
    if item not in cats:
        cats.append(item)

person_cols = results[list(results.keys())[0]].loc[:,:'1.1.1 Bread and cereals'].columns.tolist()[:-1]

for item in results[list(results.keys())[0]].columns:
    if item not in person_cols and item not in list(cat_dict.keys()):
        cat_dict[item] = 'Other_co2'


grouping_var_main = ['household_comp', 'age_group']
grouping_vars = ['dwelling_type', ' '] # 'gender', 'occupancy_rate', 'disability_care', 'disability_mobility',

aggregated_data = pd.DataFrame()
for year in years:
    temp = results[str(year)].rename(columns=cat_dict).sum(axis=1, level=0).drop('Other_co2', axis=1)
    temp['year'] = year
    temp[' '] = ' '
    temp['pop'] = temp['weight'] * temp['OECD scale']

    
    temp[cats] = temp[cats].apply(lambda x: x*temp['weight'])
    temp['count'] = 1
    
    aggregated_data = aggregated_data.append(temp)

aggregated_mean =  pd.DataFrame()
for item in grouping_vars:
    for year in ['year', 'No year']:
        temp2 = cp.copy(aggregated_data)
        temp2['No year'] = 'All'
        temp2 = temp2.groupby(grouping_var_main + [item, year]).sum()
        temp2[cats] = temp2[cats].apply(lambda x: x/temp2['pop'])
        temp2 = temp2[['count', 'pop'] + cats].reset_index()
        temp2['grouping'] = ', '.join(grouping_var_main + [item])
        temp2['pct_count'] = temp2['count'] / temp2['count'].sum() * 100
        temp2['pct_pop'] = temp2['pop'] / temp2['pop'].sum() * 100
        aggregated_mean = aggregated_mean.append(temp2)
  
aggregated_mean = aggregated_mean.fillna('All').drop(['No year', ' '], axis=1)
