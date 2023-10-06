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

years = list(range(2001, 2020))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables.csv', header = 0).fillna(0)
coicop_lookup_dict = dict(zip(coicop_lookup['Coicop_3'], coicop_lookup['Desc_full']))

lcfs = {year: lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/') for year in years}

count = pd.DataFrame()
# add household composition for households of interest
for year in years:
    spend_data = lcfs[year].loc[:,'1.1.1.1.1':]
    # extract spend for fuel poverty indicator
    energy_spend = spend_data.loc[:,'4.5.1.1.1.1':'4.5.5.1.1']
    # convert spend to coicop 3
    energy_spend = energy_spend.rename(columns = dict(zip(coicop_lookup['Coicop_full'], coicop_lookup['Coicop_3']))).sum(axis=1, level=0)
    energy_spend.columns = ['spend_' + x + '_' + coicop_lookup_dict[x] for x in energy_spend.columns]
    # socio-emographic vaiables
    person_data = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    
    # add single/couple variable
    person_data['household_type'] = 'Other'
    person_data.loc[(person_data['no_people'] == 1), 'household_type'] = 'single'
    person_data.loc[(person_data['no_people'] == 2) & (person_data['partners_spouses'] == 1), 'household_type'] = 'couple'
    person_data.loc[(person_data['age_youngest'] < 65), 'household_type'] = 'Other' # make 'other' for households not studies
    
    # add age variable - everyone is aged 65+, but at least one person in under 75
    person_data['age_group'] = 'Other'
    person_data.loc[(person_data['age_youngest'] >= 65) & (person_data['age_youngest'] < 75), 'age_group'] = '65+'
    person_data.loc[(person_data['age_youngest'] >= 75), 'age_group'] = '75+'
    person_data.loc[(person_data['no_people'] > 2), 'age_group'] = 'Other' # make 'other' for households not studied
    
    # room occupancy variable
    person_data['rooms_per_person'] = person_data['rooms used solely by household'] / person_data['no_people']
    
    # add gender variable for single housheolds studied
    person_data['gender'] = [''.join(x) for x in person_data['gender_all']]
    person_data.loc[(person_data['no_people'] > 1) | (person_data['age_youngest'] < 65), 'gender'] = 'Other' # make 'other' for households not studied
    
    # filter relevant columns
    person_data = person_data[['home_ownership', 'rooms in accommodation', # general demographic
                               'GOR', 'OA class 3',  # geographic
                               'household_type', 'age_group', 'gender', 'rooms_per_person', 'category of dwelling', # analytical demographic
                               'income tax', 'Income anonymised', # income
                               'weight', 'no_people', 'OECD scale']] # analytical
    
    # save to lcfs
    lcfs[year] = person_data.join(energy_spend).join(spend_data)

count = count.set_index(['household_type', 'age_group', 'gender', 'rooms_per_person', 'category of dwelling', 'year']).unstack(level='year').fillna(0)
count.to_csv(output_path + 'outputs/detailed_survey_counts.csv')    

### CONTINUE HERE!!

# save data - this is already multiplied by weight
for year in years:
    lcfs[year].to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv')