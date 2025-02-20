#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 2023

Import hhld expenditure data and adjust physical units 2001-2018

@author: lenakilian
"""

import pandas as pd
import LCFS_import_data_function as lcfs_import
import sys
import pathlib
#import math
#import numpy as np

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

data_path = 'O:/UKMRIO_Data/data/'
output_path = 'O:/geolki/Ageing/'


years = list(range(2015, 2020))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables_Ogy.csv', header = 0).fillna(0)
coicop_lookup_dict = dict(zip(coicop_lookup['Coicop_3'], coicop_lookup['Desc_full']))

lcfs = {}
for year in years:
    lcfs[year] = lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/');
    print(year)
    

# add household composition for households of interest
for year in years:
    spend_data = lcfs[year].loc[:,'1.1.1.1.1':].apply(lambda x: x*(365.25/7))

    # socio-demographic vaiables
    person_data = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    
    # filter relevant columns
    person_data = person_data[['GOR', 'OA class 3',  # geographic
                               'age hrp', 'category of dwelling', 'gender_age_all', # analytical demographic # 'gender', 'occupancy_rate', 'disability_care', 'disability_mobility'
                               'income tax', 'Income anonymised', 'home_ownership', 'rooms in accommodation', 'rooms used solely by household', # general demographic
                               'weight', 'no_people', 'OECD scale',
                               'Sampling month', 'Composition of Household',
                               'Socio-economic group - HRP', 'Gas Electric supplied to accomodation',
                               'Cars and vans in household']] # analytical

    # save data - this is already multiplied by weight
    temp = person_data.join(spend_data)#.join(energy_spend)
    temp.to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '_Ogy.csv')
    
print(sys.argv[0])