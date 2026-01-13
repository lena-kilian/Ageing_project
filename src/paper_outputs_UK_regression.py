#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import copy as cp
import statsmodels.api as sm

# set working directory
# make different path depending on operating system

output_path = 'O:/geolki/Ageing/'
plot_path = 'C:/Users/geolki/OneDrive - Universiteit Leiden/Projects/2023_Ageing project/analysis/'

years = [2019]

width_scale = 0.4
space = 0.2


plot_cols = ['#E1812C', '#3274A1']

results = {}; expenditure = {}; count = {}
for year in years:
    results[year] = pd.read_excel(output_path + 'outputs/CO2_by_hhds.xlsx', sheet_name=str(year), index_col='case')
    expenditure[year] = pd.read_excel(output_path + 'outputs/EXP_by_hhds.xlsx', sheet_name=str(year), index_col='case')
    count[year] = results[year].groupby(['household_comp', 'age_group']).count()[['GOR']]

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
 
# aggregate
results_all['domestic_energy_co2'] = results_all[cats_co2].sum(1)
results_all['domestic_energy_spend'] = results_all[cats_spend].sum(1)
 
# Income 
income_groups = list(range(0, 100, 15))
uk_dict = {}
results_all['Income anonymised'] = results_all['Income anonymised'] * (365.25/7) / 1000
results_all['Income'] = 'more than ' + str(income_groups[-1])
results_all['Income Group'] = 6
for i in range(len(income_groups[:-1])):
    results_all.loc[(results_all['Income anonymised'] >= income_groups[i]) & (results_all['Income anonymised'] < income_groups[i+1]), 'Income'] = str(income_groups[i]) + '-' +  str(income_groups[i+1])
    results_all.loc[(results_all['Income'] == str(income_groups[i]) + '-' +  str(income_groups[i+1])), 'Income Group'] = i

results_all['Income_pc'] = results_all['Income anonymised'] / results_all['no_people']
results_all['rooms_pc'] = results_all['rooms in accommodation'] / results_all['no_people']

#########################
## Regression analysis ##
#########################

keep = ['age_group', 'no_people', 'Income anonymised', 'rooms in accommodation', 'domestic_energy_co2', 'domestic_energy_spend']

data = results_all[keep]

#dummies_income = pd.get_dummies(data['Income']).astype(float)
dummies_age = pd.get_dummies(data['age_group']).astype(float).drop(['younger'], axis=1)

data = data.join(dummies_age).drop(['age_group'], axis=1)

x = data.drop(['domestic_energy_co2', 'domestic_energy_spend'], axis=1)
x = sm.add_constant(x)


# CO2
y_co2 = data['domestic_energy_co2']
model_co2 = sm.OLS(y_co2, x).fit()
model_co2_robust_ses = model_co2.get_robustcov_results(cov_type="HC2")
print(model_co2_robust_ses.summary())

# Spend
y_spend = data['domestic_energy_spend']
model_spend = sm.OLS(y_spend, x).fit()
model_spend_robust_ses = model_spend.get_robustcov_results(cov_type="HC2")
print(model_spend_robust_ses.summary())

