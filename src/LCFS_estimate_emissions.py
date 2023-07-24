#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import estimate_emissions_main_function as estimate_emissions
from sys import platform
import pathlib
import copy as cp

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if platform[:3] == 'win' and 'ds.leeds.ac.uk' in path:
    data_path = 'O:/UKMRIO_Data/data/model_inputs/'
elif platform[:3] == 'win' and 'ds.leeds.ac.uk' not in path:
    data_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'
else:
    data_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2017, 2020))

# load LFC data
lcfs = {year: pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv', index_col=0) for year in years}
people = {}; hhdspend={}
for year in years:
    people[year] = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    hhdspend[year] = lcfs[year].loc[:,'1.1.1.1.1':'12.7.1.1.6'].astype(float).apply(lambda x: x*lcfs[year]['weight'])
  
# calculate emissions
hhd_ghg, multipliers = estimate_emissions.make_footprint(hhdspend, data_path)

# save product names
idx = hhd_ghg[years[0]].columns.tolist()

# calculate emission for individual households
for year in years:
    hhd_ghg[year] = hhd_ghg[year].apply(lambda x: x/people[year]['weight'])
    hhd_ghg[year] = people[year].join(hhd_ghg[year])
    
# save household results
with pd.ExcelWriter(output_path + 'outputs/GHG_by_hhds.xlsx') as writer:
    for year in years:
        hhd_ghg[year].to_excel(writer, sheet_name=str(year))

# calculate emissions from groups
results = {}; results['hhd_type_1'] = pd.DataFrame(); results['hhd_type_2'] = pd.DataFrame()
for year in years:
    temp = hhd_ghg[year]
    temp['pop'] = temp['weight'] * temp['no_people']
    temp['pop_OECD'] = temp['weight'] * temp['OECD scale']
    temp[idx] = temp[idx].apply(lambda x: x* temp['weight'])
    
    for hhd_type in ['hhd_type_1', 'hhd_type_2']:
        temp2 = cp.copy(temp)
        temp2 = temp2.groupby([hhd_type, hhd_type + '_sex']).sum()
        temp2.index.names = ['hhd_type', 'hhd_sex_composition']
        # correct number of people again
        temp2['no_people'] = temp2['pop'] / temp2['weight']
        temp2['OECD scale'] = temp2['pop_OECD'] / temp2['weight']
        # calculate per household emissions
        temp2[idx] = temp2[idx].apply(lambda x: x/temp2['pop_OECD'])
        # add identifying variable
        temp2['year'] = year
        # save relevant variable
        keep = ['hhd_type', 'hhd_sex_composition', 'year', 'weight', 'no_people', 'OECD scale']
        results[hhd_type] = results[hhd_type].append(temp2.reset_index()[keep + idx])

# add count data
# import count data
counts = pd.read_csv(output_path + 'outputs/detailed_survey_counts.csv', header=[0, 1], index_col=[0, 1, 2]).stack(level='year').reset_index()
counts['year'] = counts['year'].astype(int)

for hhd_type in ['hhd_type_1', 'hhd_type_2']:
    # add count data
    temp = counts.loc[counts['group'] == hhd_type]
    results[hhd_type] = temp.merge(results[hhd_type], on =['hhd_type', 'hhd_sex_composition', 'year'])


with pd.ExcelWriter(output_path + 'outputs/GHG_by_hhd_types.xlsx') as writer:
    for hhd_type in ['hhd_type_1', 'hhd_type_2']:
        results[hhd_type].to_excel(writer, sheet_name=hhd_type)

check = results['hhd_type_1'].set_index(['year', 'hhd_type'])
check = check[idx].sum(1)
