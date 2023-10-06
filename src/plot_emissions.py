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
import copy as cp

# set working directory
# make different path depending on operating system

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

results = pd.read_excel(output_path + 'outputs/GHG_by_hhds.xlsx', sheet_name=None, index_col='case')

# keep only categories linked to fuel burning in home; electricity; personal travel

cat_dict = {'4.5.1 Electricity':'Electricity', '4.5.2 Gas':'Gas', 
            '4.5.3 Liquid fuels':'Other home energy', '4.5.4 Solid fuels':'Other home energy', '4.5.5 Heat energy':'Other home energy',  
            '7.2.1 Spare parts and accessories for personal transport equipment':'Personal transport equipment',
            '7.2.2 Fuels and lubricants for personal transport equipment':'Personal transport fuel',
            '7.2.3 Maintenance and repair of personal transport equipment':'Personal transport equipment',
            '7.2.4 Other services in respect of personal transport equipment':'Personal transport equipment'}

cats = []
for item in list(cat_dict.values()):
    if item not in cats:
        cats.append(item)

person_cols = results[list(results.keys())[0]].loc[:,:'1.1.1 Bread and cereals'].columns.tolist()[:-1]

for item in results[list(results.keys())[0]].columns:
    if item not in person_cols and item not in list(cat_dict.keys()):
        cat_dict[item] = 'Other_ghg'
    

aggregated = pd.DataFrame()
for year in range(2005, 2020):
    temp = results[str(year)].rename(columns=cat_dict).sum(axis=1, level=0).drop('Other_ghg', axis=1)\
        .set_index(['household_comp', 'age_group', 'gender', 'dwelling_type'])
    temp['pop'] = temp['weight'] * temp['OECD scale']
    
    temp[cats + ['rooms_per_person']] = temp[cats + ['rooms_per_person']].apply(lambda x: x*temp['pop'])
    temp['count'] = 1
    temp = temp.sum(axis=0, level=['household_comp', 'age_group', 'gender', 'dwelling_type'])\
        [['pop', 'rooms_per_person', 'count'] + cats]
    temp[cats + ['rooms_per_person']] = temp[cats + ['rooms_per_person']].apply(lambda x: x/temp['pop'])

    temp = temp.reset_index()
    
    temp.loc[temp['gender'] == 'Other', 'gender'] = ''
    temp['household_comp'] = temp['household_comp'] + '_' + temp['gender']
    
    temp['None'] = '.'
    
    temp2 = cp.copy(temp)
    
    for item in ['None', 'household_comp', 'dwelling_type']:
        temp = cp.copy(temp2)
        temp['household_type'] = temp['age_group'] + '_' + temp[item] 
        temp = temp.set_index('household_type')[cats + ['rooms_per_person']].stack().reset_index().rename(columns={'level_1':'product', 0:'ghg'})
        
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,5))
        sns.barplot(ax=ax, data=temp.sort_values(['household_type', 'product']), 
                                                  x='product', y='ghg', hue='household_type', errorbar=None)
        plt.xticks(rotation=90); plt.legend(bbox_to_anchor=(1,1))
        plt.show()
