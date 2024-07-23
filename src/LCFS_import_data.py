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


years = list(range(2017, 2020))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables.csv', header = 0).fillna(0)
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
    
    # add single/couple variable
    person_data['household_comp'] = 'other'
    person_data.loc[(person_data['no_people'] == 1), 'household_comp'] = 'single'
    person_data.loc[(person_data['age_youngest'] > 17) & 
                    (person_data['no_people'] == 2) & 
                    (person_data['partners_spouses'] > 0), 'household_comp'] = 'couple'

    
    # add age variable - everyone is aged 65+, but at least one person in under 75
    person_data['age_group'] = 'younger'
    person_data.loc[(person_data['age_youngest'] >= 65), 'age_group'] = '65+'
    person_data.loc[(person_data['age_youngest'] >= 65) & (person_data['age_oldest'] >= 75), 'age_group'] = '75+'
    
    
    # add age variable - everyone is aged 65+, but at least one person in under 75
    person_data['age_hrp'] = 'younger'
    person_data.loc[(person_data['age hrp'] >= 65), 'age_hrp'] = '65+'
    person_data.loc[(person_data['age hrp'] >= 75), 'age_hrp'] = '75+'
   
    # add 'other' to not studied groups for dwelling
    person_data['dwelling_type'] = person_data['category of dwelling']
 
    # filter relevant columns
    person_data = person_data[['GOR', 'OA class 3',  # geographic
                               'household_comp', 'age_group', 'age_hrp', 'dwelling_type', 'age_oldest', 'age_youngest', # analytical demographic # 'gender', 'occupancy_rate', 'disability_care', 'disability_mobility'
                               'income tax', 'Income anonymised', 'home_ownership', 'rooms in accommodation', 'rooms used solely by household', # general demographic
                               'weight', 'no_people', 'OECD scale']] # analytical
    
    # save data - this is already multiplied by weight
    temp = person_data.join(spend_data)#.join(energy_spend)
    temp.to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv')
    
print(sys.argv[0])