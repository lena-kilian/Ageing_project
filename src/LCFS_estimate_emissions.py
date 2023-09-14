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

years = list(range(2001, 2020))

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
hhd_ghg2 = {}
for year in years:
    hhd_ghg[year] = hhd_ghg[year].fillna(0)
    hhd_ghg2[year] = hhd_ghg[year].apply(lambda x: x/people[year]['weight'])
    hhd_ghg2[year] = people[year].join(hhd_ghg2[year])
    
# save household results
with pd.ExcelWriter(output_path + 'outputs/GHG_by_hhds.xlsx') as writer:
    for year in years:
        temp = hhd_ghg2[year].drop('hhd_type_1', axis=1).rename(columns={'hhd_type_2':'hhd_type'})
        temp.to_excel(writer, sheet_name=str(year))
