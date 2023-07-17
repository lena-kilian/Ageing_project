#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 2023

Import hhld expenditure data and adjust physical units 2001-2018

@author: lenakilian
"""

import pandas as pd
import LCFS_import_data_function as lcfs_import
import copy as cp
import numpy as np
from sys import platform
import pathlib

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if platform[:3] == 'win' and 'ds.leeds.ac.uk' in path:
    data_path = 'O:/UKMRIO_Data/data/'
elif platform[:3] == 'win' and 'ds.leeds.ac.uk' not in path:
    data_path = 'C:/Users/geolki/Documents/Analysis/data/'
else:
    data_path = r'/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/data/'
    
output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2017, 2020))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables.csv', header = 0).fillna(0)

lcfs = {year: lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/') for year in years}

# add household composition for households of interest
for year in years:
    person_data = lcfs[year].loc[:,:'1.1.1'].iloc[:,:-1]
    spend_data = lcfs[year].loc[:,'1.1.1':]
    # add SPH variable
    person_data['single'] = (person_data['no_people'] == 1)
    # add couple variable
    person_data['couple'] = ((person_data['partners_spouses'] == 1) & (person_data['no_people'] == 2))
    # add age variable
    person_data['65+'] = (person_data['age_youngest'] >= 65)
    person_data['65-74'] = ((person_data['age_youngest'] >= 65) & (person_data['age_oldest'] < 75))
    person_data['75+'] = (person_data['age_youngest'] >= 75)
    
    # combine these variables
    for status in ['single', 'couple']:
        for age in ['65+', '65-74', '75+']:
            person_data[status + '_' + age] = ((person_data[status] == True) & (person_data[age] == True))

### CONTINUE HERE!!

# save data
[]