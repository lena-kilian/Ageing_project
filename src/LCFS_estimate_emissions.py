#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import estimate_emissions_main_function as estimate_emissions
import sys
import pathlib
import copy as cp

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if sys.platform[:3] == 'win':
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
keep = {'4.5.1':'4.5.1 Electricity', '4.5.2':'4.5.2 Gas', '4.5.3':'4.5.3 Liquid fuels', '4.5.4':'4.5.4 Solid fuels', '4.5.5':'4.5.5 Heat energy', 
        '7.2.2':'7.2.2 Fuels and lubricants for personal transport equipment'}

region_dict = {1:'North East', 2:'North West and Merseyside', 3:'Yorkshire and the Humber', 4:'East Midlands',
               5:'West Midlands', 6:'Eastern', 7:'London', 8:'South East', 9:'South West', 10:'Wales',
               11:'Scotland', 12:'Northern Ireland'}

hhd_exp = {}
for year in years:
    temp = cp.copy(hhdspend[year])
    temp.columns = [x.split('.')[0] + '.' + x.split('.')[1] + '.' + x.split('.')[2] for x in temp.columns]
    temp = temp.sum(axis=1, level=0)[list(keep.keys())].rename(columns=keep)
    temp = temp.apply(lambda x: x/people[year]['weight'])
    hhd_exp[year] = temp

# save product names
idx = hhd_co2[years[0]].columns.tolist()

# calculate emission for individual households
for year in years:
    hhd_co2[year] = hhd_co2[year].fillna(0).apply(lambda x: x/people[year]['weight'])
    hhd_co2[year] = people[year].join(hhd_co2[year])


output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'
# save household results
with pd.ExcelWriter(output_path + 'outputs/CO2_by_hhds.xlsx') as writer:
    for year in years:
        hhd_co2[year].to_excel(writer, sheet_name=str(year))
        print(year)
        
        
with pd.ExcelWriter(output_path + 'outputs/EXP_by_hhds.xlsx') as writer:
    for year in years:
        hhd_exp[year].to_excel(writer, sheet_name=str(year))
        print(year)
        
print(sys.argv[0])
