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
import copy as cp

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
    # add SPH variable
    person_data['single'] = (person_data['no_people'] == 1)
    # add couple variable
    person_data['couple'] = ((person_data['partners_spouses'] == 1) & (person_data['no_people'] == 2))
    # add age variable
    person_data['65+'] = ((person_data['age_youngest'] >= 65) & (person_data['age_youngest'] < 75)) # everyone is aged 65+, but at least one person in under 75
    person_data['65-74'] = ((person_data['age_youngest'] >= 65) & (person_data['age_oldest'] < 75)) # everyone is aged 65-74
    person_data['75+'] = (person_data['age_youngest'] >= 75) # everyone is aged 75+
    
    # combine these variables
    for status in ['single', 'couple']:
        for age in ['65+', '65-74', '75+']:
            person_data[status + '_' + age] = ((person_data[status] == True) & (person_data[age] == True))
            person_data.loc[person_data[status + '_' + age] == True, status + '_' + age] = status + '_' + age
            person_data.loc[person_data[status + '_' + age] == False, status + '_' + age] = ''
            
    person_data['hhd_type_1'] = person_data[['single_65-74', 'single_75+', 'couple_65-74', 'couple_75+']].sum(1)
    person_data.loc[person_data['hhd_type_1'] == '', 'hhd_type_1'] = 'Other'
    
    person_data['hhd_type_2'] = person_data[['single_65+', 'single_75+', 'couple_65+', 'couple_75+']].sum(1)
    person_data.loc[person_data['hhd_type_2'] == '', 'hhd_type_2'] = 'Other'
    
    # change gender_all column
    temp = []
    for x in person_data['gender_all']:
        new = ''
        for i in range(len(x)):
            new += str(x[i]) + '_'
        temp.append(new[:-1])
            
    person_data['gender_all'] = temp
    person_data.loc[person_data['no_people'] == 2, 'gender_all'] = 'NA'
    person_data['hhd_type_1_gender'] = person_data['gender_all']
    person_data.loc[(person_data['hhd_type_1'] == 'Other'), 'hhd_type_1_gender'] = 'Other'
    person_data['hhd_type_2_gender'] = person_data['gender_all']
    person_data.loc[(person_data['hhd_type_2'] == 'Other'), 'hhd_type_2_gender'] = 'Other'
    
    person_data['quarter'] = 'Q' + person_data['quarter'].astype(str).str[0]
    
    # filter relevant columns
    person_data = person_data[['ethnicity hrp', 'ethnicity partner hrp', 'age_all', 'gender_all',  'home_ownership', 'rooms in accommodation', 'quarter', # general demographic
                               'GOR', 'OA class 1', 'OA class 2', 'OA class 3',  # geographic
                               'hhd_type_1', 'hhd_type_2', 'hhd_type_1_gender', 'hhd_type_2_gender', # analytical demographic
                               'income tax', 'Income anonymised', # income
                               'weight', 'no_people', 'OECD scale']] # analytical
    
    # add to count DF for summary
    for hhd_type in ['hhd_type_1', 'hhd_type_2']:
        temp = cp.copy(person_data)
        temp[hhd_type] = temp[hhd_type] + '_' + temp['quarter']
        temp = temp.groupby([hhd_type, hhd_type + '_gender']).count().iloc[:,:1].reset_index()
        temp.columns = ['hhd_type', 'hhd_gender_composition', 'count'] 
        temp['year'] = year; temp['group'] = hhd_type
        
        count = count.append(temp)
    
    # save to lcfs
    lcfs[year] = person_data.join(energy_spend).join(spend_data)

count = count.set_index(['group', 'hhd_type', 'hhd_gender_composition', 'year']).unstack(level='year').fillna(0)
count.to_csv(output_path + 'outputs/detailed_survey_counts.csv')    

### CONTINUE HERE!!

# save data - this is already multiplied by weight
for year in years:
    lcfs[year].to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv')