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
elif platform[:3] == 'win' and 'ds.leeds.ac.uk' not in path:
    data_path = 'C:/Users/geolki/Documents/Analysis/data/'
else:
    data_path = r'/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/data/'
    
output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2001, 2020))

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
    
    # # extract spend for fuel poverty indicator
    # energy_spend = spend_data.loc[:,'4.5.1.1.1.1':'4.5.5.1.1']
    # # convert spend to coicop 3
    # energy_spend = energy_spend.rename(columns = dict(zip(coicop_lookup['Coicop_full'], coicop_lookup['Coicop_3']))).sum(axis=1, level=0)
    # energy_spend.columns = ['spend_' + x + '_' + coicop_lookup_dict[x] for x in energy_spend.columns]
    
    # socio-emographic vaiables
    person_data = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    
    # add single/couple variable
    person_data['household_comp'] = 'Other'
    person_data.loc[(person_data['no_people'] == 1), 'household_comp'] = 'single'
    person_data.loc[(person_data['no_people'] == 2) & (person_data['partners_spouses'] == 1), 'household_comp'] = 'couple'
    person_data.loc[(person_data['age_youngest'] < 65), 'household_comp'] = 'Other' # make 'other' for households not studies
    
    # add age variable - everyone is aged 65+, but at least one person in under 75
    person_data['age_group'] = 'Other'
    person_data.loc[(person_data['age_youngest'] >= 65) & (person_data['age_youngest'] < 75), 'age_group'] = '65+'
    person_data.loc[(person_data['age_youngest'] >= 75), 'age_group'] = '75+'
    person_data.loc[(person_data['no_people'] > 2), 'age_group'] = 'Other' # make 'other' for households not studied
    
    # room occupancy variable
    person_data['occupancy_rate'] = 'Adequately/Over_occupied'
    person_data.loc[person_data['rooms used solely by household'] - person_data['no_people'] > 2, 'occupancy_rate'] = 'Under_occupied'    
    '''
    # use EU definition https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Under-occupied_dwelling
    """
    For statistical purposes, a dwelling is defined as under-occupied if the household living in it has at its disposal more than 
    the minimum number of rooms considered adequate, and equal to:

    one room for the household;
    one room per couple in the household;
    one room for each single person aged 18 or more;
    one room per pair of single people of the same gender between 12 and 17 years of age;
    one room for each single person between 12 and 17 years of age and not included in the previous category;
    one room per pair of children under 12 years of age.
    """
    temp = pd.DataFrame(person_data['gender_age_all'].to_list()); temp.index = person_data.index
    temp = temp.stack().reset_index().rename(columns={0:'gender_age'}).drop('level_1', axis=1)
    temp['gender'] = [x.split('_')[0] for x in temp['gender_age']]
    age = []
    for x in temp['gender_age']:
        a = str(x).split('_')[1]
        if a == 'nan':
            age.append(np.nan)
        else:
            age.append(int(float(a)))
    temp['age'] = age
    # split variables
    temp['age_group'] = '0-11'
    temp.loc[(temp['age'] >= 12) & (temp['age'] < 18), 'age_group'] = '12-17'
    temp.loc[(temp['age'] >= 18), 'age_group'] = '18+'
    # use NA for gender where it does not matter
    temp.loc[(temp['age_group'] != '12-17'), 'gender'] = 'NA'
    # count people
    temp['count'] = 1
    temp = temp.groupby(['case', 'gender', 'age_group']).sum()[['count']].unstack(['age_group', 'gender']).fillna(0).droplevel(axis=1, level=0)
    # account for minors sharing rooms
    for item in [('0-11', 'NA'), ('12-17',  'M'), ('12-17',  'W')]:
        temp[item] = [math.ceil(x/2) for x in temp[item]]
    temp['rooms_minors'] = temp[[('0-11', 'NA'), ('12-17',  'M'), ('12-17',  'W')]].sum(1)
    # account for couples sharing rooms
    temp = temp.join(person_data[['partners_spouses']])
    temp['rooms_adults'] = temp[('18+', 'NA')]
    temp.loc[temp['partners_spouses'] == 1, 'rooms_adults'] = temp['rooms_adults'] - 1
    # account for communal space
    temp['rooms_communal'] = 1
    # compare to actual number of rooms available for households
    temp = temp[['rooms_communal', 'rooms_adults', ('rooms_minors', '')]].join(person_data[['rooms used solely by household']])
    # define occupancy
    temp['occupancy'] = temp['rooms used solely by household'] - temp[['rooms_communal', 'rooms_adults', ('rooms_minors', '')]].sum(1)
    temp['occupancy_rate'] = 'Adequately_occupied'
    temp.loc[temp['occupancy'] < 0, 'occupancy_rate'] = 'Over_occupied'
    temp.loc[temp['occupancy'] > 0, 'occupancy_rate'] = 'Under_occupied'
    # add to person_data
    person_data = person_data.join(temp[['occupancy_rate']])
    '''
    
    # add gender variable for single households studied
    person_data['gender'] = [''.join(x) for x in person_data['gender_all']]
    person_data.loc[(person_data['no_people'] > 1) | (person_data['age_youngest'] < 65), 'gender'] = 'Other' # make 'other' for households not studied
    
    # add 'other' to not studied groups for dwelling
    person_data['dwelling_type'] = person_data['category of dwelling']
    person_data.loc[(person_data['household_comp'] == 'Other'), 'dwelling_type'] = 'Other'
    
    if year >= 2013:
        # add disability allowance variable for households studied
        person_data['disability_mobility'] = False
        person_data.loc[(person_data['disability allowance type'] == 2) | (person_data['disability allowance type'] == 3), 'disability_mobility'] = True
        
        person_data['disability_care'] = False
        person_data.loc[(person_data['disability allowance type'] == 1) | (person_data['disability allowance type'] == 3), 'disability_care'] = True
       
        person_data.loc[(person_data['household_comp'] == 'Other'), 'disability_care'] = False
        person_data.loc[(person_data['household_comp'] == 'Other'), 'disability_mobility'] = False
    else:
        person_data['disability_care'] = 'NA'
        person_data['disability_mobility'] = 'NA'
        
    
    # filter relevant columns
    person_data = person_data[['GOR', 'OA class 3',  # geographic
                               'household_comp', 'age_group', 'gender', 'occupancy_rate', 'dwelling_type', 'disability_care', 'disability_mobility', # analytical demographic
                               'income tax', 'Income anonymised', 'home_ownership', 'rooms in accommodation', 'rooms used solely by household', # general demographic
                               'weight', 'no_people', 'OECD scale']] # analytical
    
    # save data - this is already multiplied by weight
    temp = person_data.join(spend_data)#.join(energy_spend)
    temp.to_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv')