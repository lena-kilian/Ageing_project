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

pop = 'no_people' #'OECD scale'

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
    
results_all = pd.DataFrame()
for year in years:
    temp = cp.copy(results[year])
    temp['year'] = year
    results_all = results_all.append(temp)

survey_count = results_all.groupby(['hhd_comp_X_age']).count()[['GOR']]


### check spend vs emissions
for item in ['Gas', 'Electricity', 'Other home energy']:
    sns.scatterplot(data=results_all, x=item, y='Spend_' + item, hue='hhd_comp_X_age')
    plt.xlim(0, 10); plt.ylim(0, 100)
    plt.legend(bbox_to_anchor=(1,1))
    plt.show()
    
corr_cats = ['Electricity', 'Gas', 'Spend_Electricity', 'Spend_Gas']

corr1 = results_all[corr_cats].corr()
corr2 = results_all[['year'] + corr_cats].groupby('year').corr().unstack(level=1)[[('Gas', 'Spend_Gas'), ('Electricity', 'Spend_Electricity')]]
corr3 = results_all[['year', 'hhd_comp_X_age'] + corr_cats].groupby(['year', 'hhd_comp_X_age']).corr().unstack(level=2)[[('Gas', 'Spend_Gas'), ('Electricity', 'Spend_Electricity')]]


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

temp = cp.copy(results_all)
temp['pop'] = temp[pop] * temp['weight']
temp[cats_co2] = temp[cats_co2].apply(lambda x: x*temp['weight'])
temp = temp.groupby(['household_comp']).sum()
temp[cats_co2] = temp[cats_co2].apply(lambda x: x/temp['pop'])
temp = temp[cats_co2].reset_index()
temp['year'] = year

results_hhld_comp_co2 = results_hhld_comp_co2.append(temp)
    
results_hhld_comp_co2['domestic_energy'] = results_hhld_comp_co2['Electricity'] + results_hhld_comp_co2['Gas'] + results_hhld_comp_co2['Other home energy']
temp = results_hhld_comp_co2
sns.barplot(data=temp, x='household_comp', y='domestic_energy'); plt.title('2017-2019'); plt.ylabel('Domestic Emissions per Capita (tCO2/capita)'); plt.xlabel(''); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_co2.png', dpi=200, bbox_inches='tight'); plt.show()
    
    
# Spend by household_comp (single, couple, other)

results_hhld_comp_exp = pd.DataFrame()
temp = cp.copy(results_all)
temp['pop'] = temp[pop] * temp['weight']
temp[cats_spend] = temp[cats_spend].apply(lambda x: x*temp['weight'])
temp = temp.groupby(['household_comp']).sum()
temp[cats_spend] = temp[cats_spend].apply(lambda x: x/temp['pop'])
temp = temp[cats_spend].reset_index()
temp['year'] = year

results_hhld_comp_exp = results_hhld_comp_exp.append(temp)

results_hhld_comp_exp['Spend_domestic_energy'] = results_hhld_comp_exp['Spend_Electricity'] + results_hhld_comp_exp['Spend_Gas'] + results_hhld_comp_exp['Spend_Other home energy']

temp = results_hhld_comp_exp
sns.barplot(data=temp, x='household_comp', y='Spend_domestic_energy'); plt.title('2017-2019'); 
plt.ylabel('Domestic Energy Spend per Capita\n(weekly GBP/capita)'); plt.xlabel(''); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_spend.png', dpi=200, bbox_inches='tight'); plt.show()
    

# CO2 by household_comp (single, couple, other) x age

results_hhld_comp_age_co2 = pd.DataFrame()
temp = cp.copy(results_all)
temp['pop'] = temp[pop] * temp['weight']
temp[cats_co2] = temp[cats_co2].apply(lambda x: x*temp['weight'])
temp = temp.groupby(['hhd_comp_X_age']).sum()
temp[cats_co2] = temp[cats_co2].apply(lambda x: x/temp['pop'])
temp = temp[cats_co2].reset_index()
temp['year'] = year

results_hhld_comp_age_co2 = results_hhld_comp_age_co2.append(temp)

results_hhld_comp_age_co2['domestic_energy'] = results_hhld_comp_age_co2['Electricity'] + results_hhld_comp_age_co2['Gas'] + results_hhld_comp_age_co2['Other home energy']

temp = results_hhld_comp_age_co2
sns.barplot(data=temp, x='hhd_comp_X_age', y='domestic_energy', color='#4472C4'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Domestic Energy per Capita (tCO2/capita)'); plt.xlabel('') 
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_x_age_co2.png', dpi=200, bbox_inches='tight'); plt.show()
   

temp = results_hhld_comp_age_co2.set_index(['hhd_comp_X_age'])[['Electricity', 'Gas', 'Other home energy']]\
    .stack().reset_index().rename(columns={'level_1':'Source', 0:'CO2'})
sns.barplot(data=temp, x='hhd_comp_X_age', y='CO2', hue='Source'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Domestic Energy per Capita (tCO2/capita)'); plt.xlabel('') 
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_x_age_x_source_co2.png', dpi=200, bbox_inches='tight'); plt.show()
        

# Spend by household_comp (single, couple, other) x age

results_hhld_comp_age_exp = pd.DataFrame()
temp = cp.copy(results_all)
temp['pop'] = temp[pop] * temp['weight']
temp[cats_spend] = temp[cats_spend].apply(lambda x: x*temp['weight'])
temp = temp.groupby(['hhd_comp_X_age']).sum()
temp[cats_spend] = temp[cats_spend].apply(lambda x: x/temp['pop'])
temp = temp[cats_spend].reset_index()
temp['year'] = year

results_hhld_comp_age_exp = results_hhld_comp_age_exp.append(temp)

results_hhld_comp_age_exp['domestic_energy'] = results_hhld_comp_age_exp['Spend_Electricity'] + results_hhld_comp_age_exp['Spend_Gas'] + results_hhld_comp_age_exp['Spend_Other home energy']
temp = results_hhld_comp_age_exp

sns.barplot(data=temp, x='hhd_comp_X_age', y='domestic_energy', color='#4472C4'); plt.title('2017-2019'); plt.xticks(rotation=90); 
plt.ylabel('Domestic Energy Spend per Capita\n(weekly GBP/capita)'); plt.xlabel('');
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_x_age_spend.png', dpi=200, bbox_inches='tight'); plt.show()


temp = results_hhld_comp_age_exp.set_index(['hhd_comp_X_age'])[['Spend_Electricity', 'Spend_Gas', 'Spend_Other home energy']]\
    .stack().reset_index().rename(columns={'level_1':'Source', 0:'CO2'})
sns.barplot(data=temp, x='hhd_comp_X_age', y='CO2', hue='Source'); plt.title('2017-2019'); plt.xticks(rotation=90);
plt.ylabel('Domestic Energy Spend per Capita\n(weekly GBP/capita)'); plt.xlabel('') 
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(output_path + 'outputs/plots/hhld_comp_x_age_x_source_spend.png', dpi=200, bbox_inches='tight'); plt.show()
 

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

  