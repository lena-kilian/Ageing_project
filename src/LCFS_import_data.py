#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 2023

Import hhld expenditure data and adjust physical units 2001-2018

@author: lenakilian
"""

import pandas as pd
import LCFS_import_data_function as lcfs_import
from sys import platform
import pathlib
#import math
#import numpy as np

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if platform[:3] == 'win' and 'ds.leeds.ac.uk' in path:
    data_path = 'O:/UKMRIO_Data/data/'
    output_path = 'O:/geolki/Ageing/'
elif platform[:3] == 'win' and 'ds.leeds.ac.uk' not in path:
    data_path = 'C:/Users/geolki/Documents/Analysis/data/'
    output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'
else:
    data_path = r'/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/data/'
    output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'


years = list(range(2017, 2020))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables.csv', header = 0).fillna(0)
coicop_lookup_dict = dict(zip(coicop_lookup['Coicop_3'], coicop_lookup['Desc_full']))

lcfs = {}
for year in years:
    print(year)
    lcfs[year] = lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/');
    print(year)
    
#lcfs = {year: lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/') for year in years}

# add household composition for households of interest
for year in years:
    spend_data = lcfs[year].loc[:,'1.1.1.1.1':]
    
    # socio-demographic vaiables
    person_data = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    
    # add single/couple variable
    person_data['household_comp'] = 'other'
    person_data.loc[(person_data['no_people'] == 1), 'household_comp'] = 'single'
    person_data.loc[(person_data['no_people'] == 2) & (person_data['partners_spouses'] == 1), 'household_comp'] = 'couple'

    
    # add age variable - everyone is aged 65+, but at least one person in under 75
    person_data['age_group'] = 'younger'
    person_data.loc[(person_data['age_oldest'] >= 65) & (person_data['age_oldest'] < 75), 'age_group'] = '65+'
    person_data.loc[(person_data['age_youngest'] >= 65) & (person_data['age_oldest'] >= 75), 'age_group'] = '75+'
   
    # add 'other' to not studied groups for dwelling
    person_data['dwelling_type'] = person_data['category of dwelling']
 
    # filter relevant columns
    person_data = person_data[['GOR', 'OA class 3',  # geographic
                               'household_comp', 'age_group', 'dwelling_type', 'age_oldest', 'age_youngest', # analytical demographic # 'gender', 'occupancy_rate', 'disability_care', 'disability_mobility'
                               'income tax', 'Income anonymised', 'home_ownership', 'rooms in accommodation', 'rooms used solely by household', # general demographic
                               'weight', 'no_people', 'OECD scale']] # analytical
    
    # save data - this is already multiplied by weight
    temp = person_data.join(spend_data)#.join(energy_spend)
    temp.to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv')