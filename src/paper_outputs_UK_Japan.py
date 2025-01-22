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
import sys

# set working directory
# make different path depending on operating system

output_path = 'O:/geolki/Ageing/'

years = list(range(2017, 2020))

results = {}; expenditure = {}
for year in years:
    results[year] = pd.read_excel(output_path + 'outputs/CO2_by_hhds.xlsx', sheet_name=str(year), index_col='case')
    expenditure[year] = pd.read_excel(output_path + 'outputs/EXP_by_hhds.xlsx', sheet_name=str(year), index_col='case')

pop = 'no_people' # 'OECD scale' #

# keep only categories linked to fuel burning in home; electricity; personal travel
cat_dict = {'4.5.1 Electricity':'Electricity', '4.5.2 Gas':'Gas', 
            '4.5.3 Liquid fuels':'Other home energy', '4.5.4 Solid fuels':'Other home energy', '4.5.5 Heat energy':'Other home energy'}

cats_co2 = []
for item in list(cat_dict.values()):
    if item not in cats_co2:
        cats_co2.append(item)
        
cats_spend = ['Spend_' + x for x in cats_co2]

person_cols = results[list(results.keys())[0]].loc[:,:'OECD scale'].columns.tolist()

for item in results[list(results.keys())[0]].columns:
    if item not in person_cols and item not in list(cat_dict.keys()):
        cat_dict[item] = 'Other_co2'
        
# aggregate emission products

order_groups = ['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']
order_hhld_comp = ['single', 'couple', 'other']
order_age = ['younger', '65+', '75+']

for year in years:
    results[year] = results[year].rename(columns=cat_dict).sum(axis=1, level=0)
    expenditure[year] = expenditure[year].rename(columns=cat_dict).fillna(0).sum(axis=1, level=0)
    expenditure[year].columns = ['Spend_' + x for x in expenditure[year].columns.tolist()]
    
    results[year] = results[year].join(expenditure[year])
    
    results[year]['hhd_comp_X_age'] = results[year]['household_comp'] + ' ' + results[year]['age_group']
    results[year]['hhd_comp_X_age'] = pd.Categorical(results[year]['hhd_comp_X_age'], categories=order_groups, ordered=True)
    results[year]['household_comp'] = pd.Categorical(results[year]['household_comp'], categories=order_hhld_comp, ordered=True)
    results[year]['age_group'] = pd.Categorical(results[year]['age_group'], categories=order_age, ordered=True)
    results[year]['age_hrp'] = pd.Categorical(results[year]['age_hrp'], categories=order_age, ordered=True)
    
    if 'Other_co2' in results[year].columns.tolist():
        results[year] = results[year].drop('Other_co2', axis=1)
    
    
results_all = pd.DataFrame()
for year in years:
    temp = cp.copy(results[year])
    temp['year'] = year
    results_all = results_all.append(temp)

survey_count = results_all.groupby(['hhd_comp_X_age']).count()[['GOR']]

temp = cp.copy(results_all)
temp['all_home'] = temp[['Electricity', 'Gas', 'Other home energy']].sum(1) / temp['no_people']

#sns.barplot(data=temp, y='all_home', x='household_comp', hue='age_group'); plt.title('age GROUP'); plt.show()
#sns.barplot(data=temp, y='all_home', x='household_comp', hue='age_hrp'); plt.title('age HRP'); plt.show()

temp2 = temp.set_index(['all_home', 'household_comp'])[['age_hrp', 'age_group']].stack().reset_index()
temp2.columns= ['all_home', 'hhd_comp', 'age_type', 'age']
temp2['compXage'] = temp2['hhd_comp'].astype(str) + ' ' + temp2['age'].astype(str)
temp2['compXage'] = pd.Categorical(temp2['compXage'], categories=order_groups, ordered=True)

#sns.barplot(data=temp2, y='all_home', x='compXage', hue='age_type'); plt.xticks(rotation=90); plt.show()

#sns.barplot(data=temp2, y='all_home', hue='compXage', x='age_type'); plt.legend(bbox_to_anchor=(1,1)); plt.show()

#sns.barplot(data=temp2, y='all_home', hue='age', x='age_type'); plt.legend(bbox_to_anchor=(1,1)); plt.show()

#######################################
## Replicate outputs from Japan data ## 
#######################################

for value in ['co2', 'spend']:
    
    # only household comp or age
    cats = eval('cats_' + value)
    fig, axs = plt.subplots(ncols=2, figsize=(10, 5), sharey=True)
    for i in range(2):
        item = ['household_comp', 'age_group'][i]
    
        temp = cp.copy(results_all)
        temp['pop'] = temp[pop] * temp['weight']
        temp[cats] = temp[cats].apply(lambda x: x*temp['weight'])
        temp = temp.groupby([item]).sum()
        temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])
        temp = temp[cats].reset_index()
    
        temp['domestic_energy'] = temp[cats].sum(1)
        
        sns.barplot(ax=axs[i], data=temp, x=item, y='domestic_energy', color='#4472C4')
        axs[i].set_title(item.capitalize().replace('_', ' ') + ' (2017-2019)'); axs[i].set_xlabel('');
        
    if value == 'co2':
        axs[0].set_ylabel('Domestic Emissions per Capita (tCO2/capita)')
    else:
        axs[0].set_ylabel('Domestic Energy Spend per Capita')
    axs[1].set_ylabel('')

    plt.savefig(output_path + 'outputs/plots/barplot_hhdcomp_AND_age_' + value + '.png', dpi=200, bbox_inches='tight')
    plt.show()
    

    # both household_comp (single, couple, other) x age
    temp = cp.copy(results_all)
    temp['pop'] = temp[pop] * temp['weight']
    temp[cats] = temp[cats].apply(lambda x: x*temp['weight'])
    temp = temp.groupby(['hhd_comp_X_age']).sum()
    temp[cats] = temp[cats].apply(lambda x: x/temp['pop'])
    temp = temp[cats].reset_index()

    temp['domestic_energy'] = temp[cats].sum(1)
    
    sns.barplot(data=temp, x='hhd_comp_X_age', y='domestic_energy', color='#4472C4')
    plt.title('2017-2019'); plt.xticks(rotation=90); plt.xlabel('');
    
    if value == 'co2':
        plt.ylabel('Domestic Emissions per Capita (tCO2/capita)')
    else:
        plt.ylabel('Domestic Energy Spend per Capita')

    plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
    plt.savefig(output_path + 'outputs/plots/barplot_hhld_comp_X_age_' + value + '.png', dpi=200, bbox_inches='tight'); plt.show()
    
   

# share of house
results_house_type = pd.DataFrame()    
temp = cp.copy(results_all)
temp = temp.groupby(['hhd_comp_X_age', 'dwelling_type']).sum()[['weight']].unstack('dwelling_type').droplevel(axis=1, level=0)
temp['sum'] = temp.sum(1)
temp = temp.apply(lambda x: x/temp['sum'] * 100).drop('sum', axis=1).T
temp['year'] = year

results_house_type = results_house_type.append(temp)

temp = temp[['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']].T

temp.plot(kind='bar', stacked='True'); plt.title('2017-2019'); plt.xticks(rotation=90); 
plt.ylabel('Percentage of Households (%)'); plt.xlabel(''); plt.legend(bbox_to_anchor=(1,1), title='Dwelling type')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':');  
plt.savefig(output_path + 'outputs/plots/dwelling_type.png', dpi=200, bbox_inches='tight'); plt.show()


# house size (number of rooms)
results_house_size = pd.DataFrame()    
temp = cp.copy(results_all)
temp['rooms in accommodation'] = temp['rooms in accommodation'] / temp['no_people']
temp['year'] = year

results_house_size = results_house_size.append(temp[['hhd_comp_X_age', 'rooms in accommodation', 'year']])


temp = results_house_size
sns.boxplot(data=temp, x='hhd_comp_X_age', y='rooms in accommodation', color='#4472C4'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Dwelling size per Capita\n(number of rooms/capita)'); plt.xlabel('') 
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':');  
plt.savefig(output_path + 'outputs/plots/dwelling_size.png', dpi=200, bbox_inches='tight'); plt.show()


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
temp = cp.copy(results_all)
temp['Income anonymised'] = temp['Income anonymised'] * (365.25/7) / 1000
temp['Income'] = 'more than ' + str(income_groups[-1])
for i in range(len(income_groups[:-1])):
    temp.loc[(temp['Income anonymised'] >= income_groups[i]) & (temp['Income anonymised'] < income_groups[i+1]), 'Income'] = str(income_groups[i]) + '-' +  str(income_groups[i+1])
temp.loc[(temp['Income anonymised'] < 0), 'Income'] = 'unkown'


temp = temp.groupby(['hhd_comp_X_age', 'Income']).sum()[['weight']].unstack('Income').droplevel(axis=1, level=0)
temp['sum'] = temp.sum(1)
temp = temp.apply(lambda x: x/temp['sum'] * 100).drop('sum', axis=1)

results_income = results_income.append(temp)

temp.plot(kind='bar', stacked='True'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Percentage of Households (%)'); plt.xlabel(''); plt.legend(bbox_to_anchor=(1,1), title='Annual Income (1,000 GBP)')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/income.png', dpi=200, bbox_inches='tight'); plt.show()


# income  per capita
results_income_pc = pd.DataFrame()
for item in ['no_people', 'OECD scale']:
    temp = cp.copy(results_all)
    temp['Income anonymised'] = temp['Income anonymised'] * (365.25/7) / 1000 * temp['weight']
    temp['pop'] = temp['weight'] * temp[item]
    temp = temp.groupby('hhd_comp_X_age').sum()
    temp['Income anonymised'] = temp['Income anonymised'] / temp['pop']
    temp['Pop'] = item
    results_income_pc = results_income_pc.append(temp[['Pop', 'Income anonymised']].reset_index())

sns.barplot(data=results_income_pc, x='hhd_comp_X_age', y='Income anonymised', hue='Pop'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Annual Income per Capita\n(1,000 GBP/capita)'); plt.xlabel(''); plt.legend(bbox_to_anchor=(1,1), title='Number of people measure')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/income_pc.png', dpi=200, bbox_inches='tight'); plt.show()


print(sys.argv[0])
