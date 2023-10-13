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
results_agg = pd.DataFrame()
for year in list(results.keys()):
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
    

aggregated_data = pd.DataFrame()
for year in range(2005, 2020):
    temp = results[str(year)].rename(columns=cat_dict).sum(axis=1, level=0).drop('Other_ghg', axis=1)
    #temp.loc[temp['occupancy_rate'] != 'Under_occupied', 'occupancy_rate'] = 'Adequately/Over_occupied'
    temp = temp.set_index(['household_comp', 'age_group', 'gender', 'dwelling_type', 'occupancy_rate'])
    temp['pop'] = temp['weight'] * temp['OECD scale']
    
    temp[cats] = temp[cats].apply(lambda x: x*temp['weight'])
    temp['count'] = 1
    temp = temp.sum(axis=0, level=['household_comp', 'age_group', 'gender', 'dwelling_type', 'occupancy_rate'])\
        [['pop', 'count'] + cats]
    temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])

    temp = temp.reset_index()

    temp['household_comp'] = temp['household_comp'] + '_' + temp['age_group']
    
    temp['None'] = '.'
    
    temp2 = cp.copy(temp)
    temp2['grouping'] = 'All'
    temp2['year'] = year
    
    #aggregated_data = aggregated_data.append(temp2)
    
    for item in ['gender', 'household_comp', 'dwelling_type', 'occupancy_rate', 'None']:
        temp = cp.copy(temp2)
        temp[cats] = temp[cats].apply(lambda x: x*temp['pop'])
        temp = temp.groupby(item).sum().reset_index()
        temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])
        temp['grouping'] = item
        temp['year'] = year
        #aggregated_data = aggregated_data.append(temp)
    
        temp = temp.set_index([item])[cats].stack().reset_index().rename(columns={'level_1':'product', 0:'ghg'})
        
        #fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,5))
        #sns.barplot(ax=ax, data=temp.sort_values([item, 'product']), x='product', y='ghg', hue=item, errorbar=None)
        #plt.xticks(rotation=90); plt.legend(bbox_to_anchor=(1,1))
        #plt.title(str(year) + ' ' + item)
        #plt.show()
        
    grouping_var = 'household_comp'
    for item in ['gender', 'dwelling_type', 'occupancy_rate', 'None']:
        temp = cp.copy(temp2)
        temp.loc[temp['household_comp'] == 'Other_Other', item] = 'NA'
        temp[cats] = temp[cats].apply(lambda x: x*temp['pop'])
        temp = temp.groupby([item, grouping_var]).sum().reset_index()
        temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])
        temp['grouping'] = grouping_var + ', ' + item
        temp['year'] = year
        temp['count_pct'] = temp['count'] / temp['count'].sum() * 100
        aggregated_data = aggregated_data.append(temp)
    
        temp['group'] = temp[grouping_var] + '_' + temp[item]
        temp = temp.set_index(['group'])[cats].stack().reset_index().rename(columns={'level_1':'product', 0:'ghg'})
        
        if year >= 2017:
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,5))
            sns.barplot(ax=ax, data=temp.sort_values(['group', 'product']), x='product', y='ghg', hue='group', errorbar=None)
            plt.xticks(rotation=90); plt.legend(bbox_to_anchor=(1,1))
            plt.title(str(year) + ' ' + grouping_var + ' ' + item)
            plt.show()
aggregated_data = aggregated_data[['grouping', 'year', 'household_comp', 'gender', 'dwelling_type', 
                                   'occupancy_rate', 'pop', 'count', 'count_pct'] + cats].fillna('All')


for group in aggregated_data[['grouping']].drop_duplicates()['grouping']:
    temp = aggregated_data.loc[aggregated_data['grouping'] == group]
    temp['None'] = ''
    var1 = group.split(', ')[0]
    var2 = group.split(', ')[1]
    
    temp.index = list(range(len(temp.index)))
    
    if var2 == 'gender':
        temp.loc[(temp['gender'] == 'M') | (temp['gender'] == 'W'), 'gender'] = 'single ' + temp['gender']
        temp.loc[(temp['household_comp'].str.split('_').str[0] == 'couple'), 'gender'] = 'couple'
        temp['age'] = temp['household_comp'].str.split('_').str[1]
        var1 = 'age'
        
        temp = temp.sort_values([var1, var2])
    
    fig, axs = plt.subplots(nrows=2, ncols=len(cats), figsize=(7.5*len(cats),7.5))
    for c in range(len(cats)):
        product = cats[c]
        
        if c == len(cats)-1:
            legend=True
            pos_y = 1
        else:
            legend=False
            pos_y = -0.25
        
        sns.lineplot(ax=axs[0, c], data=temp, x='year', y=product, hue=var1, style=var2, legend=legend)
        axs[0, c].set_title(product)
        axs[0, c].set_ylabel('tCO2e/capita')
        
        temp2 = temp.loc[temp[var2] != 'NA']
        
        sns.barplot(ax=axs[1, c], data=temp2, x=var2, y=product, hue=var1)
        axs[1, c].tick_params(axis='x', rotation=90)
        axs[1, c].set_ylabel('tCO2e/capita')
        axs[1, c].legend(bbox_to_anchor=(1.3, pos_y))
    
    axs[0, len(cats)-1].legend(bbox_to_anchor=(1, 1))
    plt.show()
    