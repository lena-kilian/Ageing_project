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
import numpy as np

# set working directory
# make different path depending on operating system

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

results = pd.read_excel(output_path + 'outputs/CO2_by_hhds.xlsx', sheet_name=None, index_col='case')

years = list(results.keys())

expenditure = {}
for year in years:
    expenditure[year] = pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv', index_col='case').loc[:, '1.1.1.1.1':]
    expenditure[year].columns = [x.split('.')[0] + '.' + x.split('.')[1] + '.' + x.split('.')[2] for x in expenditure[year].columns]
    expenditure[year] = expenditure[year].sum(axis=1, level=0)

# keep only categories linked to fuel burning in home; electricity; personal travel
cat_dict = {'4.5.1 Electricity':'Electricity', '4.5.2 Gas':'Gas', 
            '4.5.3 Liquid fuels':'Other home energy', '4.5.4 Solid fuels':'Other home energy', '4.5.5 Heat energy':'Other home energy',  
            '7.2.2 Fuels and lubricants for personal transport equipment':'Personal transport fuel'}

cat_dict_exp = {}
for item in list(cat_dict.keys()):
    cat_dict_exp[str(item.split(' ')[0])] = cat_dict[item]

person_cols = results[list(results.keys())[0]].loc[:,:'1.1.1 Bread and cereals'].columns.tolist()[:-1]

for item in results[list(results.keys())[0]].columns:
    if item not in person_cols and item not in list(cat_dict.keys()):
        cat_dict[item] = 'Other_co2'
        
for item in expenditure[list(expenditure.keys())[0]].columns:
    if item not in list(cat_dict_exp.keys()):
        cat_dict_exp[item] = 'Other_co2'
        
# aggregate emission products

order_groups = ['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']
order_hhld_comp = ['single', 'couple', 'other']

for year in years:
    results[year] = results[year].rename(columns=cat_dict).sum(axis=1, level=0)
    expenditure[year] = expenditure[year].rename(columns=cat_dict_exp).sum(axis=1, level=0)
    expenditure[year].columns = ['Spend_' + x for x in expenditure[year].columns.tolist()]
    
    results[year] = results[year].join(expenditure[year])
    
    results[year]['hhd_comp_X_age'] = results[year]['household_comp'] + ' ' + results[year]['age_group']
    results[year]['hhd_comp_X_age'] = pd.Categorical(results[year]['hhd_comp_X_age'], categories=order_groups, ordered=True)
    results[year]['household_comp'] = pd.Categorical(results[year]['household_comp'], categories=order_hhld_comp, ordered=True)
    

#######################################
## Replicate outputs from Japan data ## 
#######################################

cats_co2 = []
for item in list(cat_dict.values()):
    if item not in cats_co2:
        cats_co2.append(item)

cats_spend = []
for item in list(cat_dict_exp.values()):
    if 'Spend_' + item not in cats_spend:
        cats_spend.append('Spend_' + item)

# CO2e by household_comp (single, couple, other)

results_hhld_comp_co2 = pd.DataFrame()
for year in years:
    temp = results[year]
    temp['pop'] = temp['no_people'] + temp['weight']
    temp[cats_co2] = temp[cats_co2].apply(lambda x: x*temp['weight'])
    temp = temp.groupby(['household_comp']).sum()
    temp[cats_co2] = temp[cats_co2].apply(lambda x: x/temp['pop'])
    temp = temp[cats_co2].reset_index()
    temp['year'] = year
    
    results_hhld_comp_co2 = results_hhld_comp_co2.append(temp)
    
results_hhld_comp_co2['domestic_energy'] = results_hhld_comp_co2['Electricity'] + results_hhld_comp_co2['Gas'] + results_hhld_comp_co2['Other home energy']
for year in years:
    temp = results_hhld_comp_co2.loc[results_hhld_comp_co2['year'] == year]
    sns.barplot(data=temp, x='household_comp', y='domestic_energy'); plt.title(str(year)); plt.show()
    
    
# Spend by household_comp (single, couple, other)

results_hhld_comp_exp = pd.DataFrame()
for year in years:
    temp = results[year]
    temp['pop'] = temp['no_people'] + temp['weight']
    temp[cats_spend] = temp[cats_spend].apply(lambda x: x*temp['weight'])
    temp = temp.groupby(['household_comp']).sum()
    temp[cats_spend] = temp[cats_spend].apply(lambda x: x/temp['pop'])
    temp = temp[cats_spend].reset_index()
    temp['year'] = year
    
    results_hhld_comp_exp = results_hhld_comp_exp.append(temp)

results_hhld_comp_exp['Spend_domestic_energy'] = results_hhld_comp_exp['Spend_Electricity'] + results_hhld_comp_exp['Spend_Gas'] + results_hhld_comp_exp['Spend_Other home energy']
for year in years:
    temp = results_hhld_comp_exp.loc[results_hhld_comp_exp['year'] == year]
    sns.barplot(data=temp, x='household_comp', y='Spend_domestic_energy'); plt.title(str(year)); plt.show()
    

# CO2 by household_comp (single, couple, other) x age

results_hhld_comp_age_co2 = pd.DataFrame()
for year in years:
    temp = results[year]
    temp['pop'] = temp['no_people'] + temp['weight']
    temp[cats_co2] = temp[cats_co2].apply(lambda x: x*temp['weight'])
    temp = temp.groupby(['hhd_comp_X_age']).sum()
    temp[cats_co2] = temp[cats_co2].apply(lambda x: x/temp['pop'])
    temp = temp[cats_co2].reset_index()
    temp['year'] = year
    
    results_hhld_comp_age_co2 = results_hhld_comp_age_co2.append(temp)

results_hhld_comp_age_co2['domestic_energy'] = results_hhld_comp_age_co2['Electricity'] + results_hhld_comp_age_co2['Gas'] + results_hhld_comp_age_co2['Other home energy']
for year in years:
    temp = results_hhld_comp_age_co2.loc[results_hhld_comp_age_co2['year'] == year]    
    sns.barplot(data=temp, x='hhd_comp_X_age', y='domestic_energy'); plt.title(str(year)); plt.xticks(rotation=90); plt.show()
    
    
# Spend by household_comp (single, couple, other) x age

results_hhld_comp_age_exp = pd.DataFrame()
for year in years:
    temp = results[year]
    temp['pop'] = temp['no_people'] + temp['weight']
    temp[cats_spend] = temp[cats_spend].apply(lambda x: x*temp['weight'])
    temp = temp.groupby(['hhd_comp_X_age']).sum()
    temp[cats_spend] = temp[cats_spend].apply(lambda x: x/temp['pop'])
    temp = temp[cats_spend].reset_index()
    temp['year'] = year
    
    results_hhld_comp_age_exp = results_hhld_comp_age_exp.append(temp)

results_hhld_comp_age_exp['domestic_energy'] = results_hhld_comp_age_exp['Spend_Electricity'] + results_hhld_comp_age_exp['Spend_Gas'] + results_hhld_comp_age_exp['Spend_Other home energy']
for year in years:
    temp = results_hhld_comp_age_exp.loc[results_hhld_comp_age_exp['year'] == year]
    sns.barplot(data=temp, x='hhd_comp_X_age', y='domestic_energy'); plt.title(str(year)); plt.xticks(rotation=90); plt.show()

# share of house
results_house_type = pd.DataFrame()    
for year in years:
    temp = results[year]
    temp = temp.groupby(['hhd_comp_X_age', 'dwelling_type']).sum()[['weight']].unstack('dwelling_type').droplevel(axis=1, level=0)
    temp['sum'] = temp.sum(1)
    temp = temp.apply(lambda x: x/temp['sum'] * 100).drop('sum', axis=1).T
    temp['year'] = year
    
    results_house_type = results_house_type.append(temp)
    
    groups = ['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']
    for item in groups:
        if item not in temp.columns.tolist():
            temp[item] = np.nan
    
    temp = temp[['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']].T
    
    temp.plot(kind='bar', stacked='True'); plt.title(str(year)); plt.xticks(rotation=90); plt.show()
    
    
# house size (number of rooms)
results_house_size = pd.DataFrame()    
for year in years:
    temp = results[year]
    temp['rooms in accommodation'] = temp['rooms in accommodation'] / temp['no_people']
    temp['year'] = year
    
    results_house_size = results_house_size.append(temp[['hhd_comp_X_age', 'rooms in accommodation', 'year']])
    
    
for year in years:
    temp = results_house_size.loc[results_house_size['year'] == year]
    sns.boxplot(data=temp, x='hhd_comp_X_age', y='rooms in accommodation'); plt.title(str(year)); plt.xticks(rotation=90); plt.show()
    


# age of dwelling - not available

income_groups = list(range(0, 100, 15))
income_names = []
start = 0
for i in income_groups:
    income_names.append(str(start) + '-' + str(i))
    start = i 
income_names = ['less than ' + str(income_groups[0])] + income_names[1:] + []

# income 
results_income = pd.DataFrame()    
for year in years:
    temp = results[year]
    temp['Income anonymised'] = temp['Income anonymised'] * (365.25/7) / 1000
    temp['Income'] = 'more than ' + str(income_groups[-1])
    for i in range(len(income_groups[:-1])):
        temp.loc[(temp['Income anonymised'] >= income_groups[i]) & (temp['Income anonymised'] < income_groups[i+1]), 'Income'] = str(income_groups[i]) + '-' +  str(income_groups[i+1])
    temp.loc[(temp['Income anonymised'] < 0), 'Income'] = 'unkown'

    temp = temp.groupby(['hhd_comp_X_age', 'Income']).sum()[['weight']].unstack('Income').droplevel(axis=1, level=0)
    temp['sum'] = temp.sum(1)
    temp = temp.apply(lambda x: x/temp['sum'] * 100).drop('sum', axis=1)
    
    results_income = results_income.append(temp)
    
    temp.plot(kind='bar', stacked='True'); plt.title(str(year)); plt.xticks(rotation=90); plt.show()
    
    
  