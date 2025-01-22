#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import estimate_emissions_main_function_Ogy as estimate_emissions
import sys
import pathlib
import copy as cp
import matplotlib.pyplot as plt

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if sys.platform[:3] == 'win':
    data_path = 'O:/UKMRIO_Data/data/model_inputs/'
    output_path = 'O:/geolki/Ageing/'
else:
    data_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'
    output_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2015, 2020))

# load LFC data
lcfs = {year: pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '_Ogy.csv', index_col=0) for year in years}
people = {}; hhdspend={}
for year in years:
    people[year] = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    hhdspend[year] = lcfs[year].loc[:,'1.1.1.1.1':'12.7.1.1.6'].astype(float) # already multiplied by weight
    
# calculate emissions
hhd_ghg, multipliers = estimate_emissions.make_footprint(hhdspend, data_path)

# calculate emissions from multipliers
region_dict = {1:'North East', 2:'North West and Merseyside', 3:'Yorkshire and the Humber', 4:'East Midlands',
               5:'West Midlands', 6:'Eastern', 7:'London', 8:'South East', 9:'South West', 10:'Wales',
               11:'Scotland', 12:'Northern Ireland'}

# calculate emission for individual households
for year in years:
    pop = people[year]['weight'] * people[year]['no_people']
    print(hhd_ghg[year].sum().sum()/pop.sum())
    ccp1 = cp.copy(hhd_ghg[year])
    ccp1.columns = [x.split('.')[0] for x in ccp1.columns]
    ccp1 = ccp1.sum(axis=1, level=0).sum(axis=0).apply(lambda x: x/pop.sum())
    ccp1.plot(kind='bar'); plt.show()
    
    hhd_ghg[year] = hhd_ghg[year].fillna(0).apply(lambda x: x/people[year]['weight'])
    hhd_ghg[year] = people[year].join(hhd_ghg[year])
    hhd_ghg[year]['GOR'] = hhd_ghg[year]['GOR'].map(region_dict)
    
    reg = cp.copy(hhd_ghg[year])
    reg.loc[:,'1.1.1 Bread and cereals':] = reg.loc[:,'1.1.1 Bread and cereals':].apply(lambda x: x*reg['weight'])
    reg['pop'] = reg['weight'] * reg['no_people']
    reg = reg.groupby('GOR').sum()
    reg.loc[:,'1.1.1 Bread and cereals':] = reg.loc[:,'1.1.1 Bread and cereals':].apply(lambda x: x/reg['pop'])
    reg = reg.loc[:,'1.1.1 Bread and cereals':].sum(axis=1)
    reg.plot(kind='bar'); plt.show()


# save household results
with pd.ExcelWriter(output_path + 'outputs/GHG_by_hhds_Ogy.xlsx') as writer:
    for year in years:
        hhd_ghg[year].to_excel(writer, sheet_name=str(year))
        print(year)
        