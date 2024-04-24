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
    output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'
else:
    data_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'
    output_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'


<<<<<<< Updated upstream
years = list(range(2017, 2020))
=======
years = list(range(2001, 2020))
>>>>>>> Stashed changes

# load LFC data
lcfs = {year: pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv', index_col=0) for year in years}
people = {}; hhdspend={}
for year in years:
    people[year] = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    hhdspend[year] = lcfs[year].loc[:,'1.1.1.1.1':'12.7.1.1.6'].astype(float) # already multiplied by weight
    
# calculate emissions
hhd_co2, multipliers = estimate_emissions.make_footprint(hhdspend, data_path)

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
