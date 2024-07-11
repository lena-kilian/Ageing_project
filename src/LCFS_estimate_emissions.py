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

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if platform[:3] == 'win':
    data_path = 'O:/UKMRIO_Data/data/model_inputs/'
    output_path = 'O:/geolki/Ageing/'
else:
    data_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'
    output_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2017, 2020))

# load LFC data
lcfs = {year: pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv', index_col=0) for year in years}
people = {}; hhdspend={}
for year in years:
    people[year] = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    hhdspend[year] = lcfs[year].loc[:,'1.1.1.1.1':'12.7.1.1.6'].astype(float) # already multiplied by weight
    
# calculate emissions
hhd_co2, multipliers = estimate_emissions.make_footprint(hhdspend, data_path)

# calculate emissions from multipliers
keep = ['4.5.1 Electricity', '4.5.2 Gas', '4.5.3 Liquid fuels', '4.5.4 Solid fuels', '4.5.5 Heat energy', 
        '7.2.2 Fuels and lubricants for personal transport equipment']
hhd_co2_2 = {}
for year in years:
    temp = cp.copy(hhdspend[year])
    temp.columns = [x.split('.')[0] + '.' + x.split('.')[1] + '.' + x.split('.')[2] for x in temp.columns]
    temp = temp.sum(axis=1, level=0)[[x.split(' ')[0] for x in keep]]
    
    temp_mult = cp.copy(multipliers[year])
    temp_mult['ccp3'] = [x.split(' ')[0] for x in temp_mult.index]
    temp_mult = temp_mult.loc[keep]
    
    temp_co2 = temp.T.apply(lambda x: x * temp_mult.set_index('ccp3')['multipliers']).fillna(0)

# save product names
idx = hhd_co2[years[0]].columns.tolist()

# calculate emission for individual households
for year in years:
    hhd_co2[year] = hhd_co2[year].fillna(0).apply(lambda x: x/people[year]['weight'])
    hhd_co2[year] = people[year].join(hhd_co2[year])
    
# save household results
with pd.ExcelWriter(output_path + 'outputs/CO2_by_hhds.xlsx') as writer:
    for year in years:
        hhd_co2[year].to_excel(writer, sheet_name=str(year))
        print(year)
