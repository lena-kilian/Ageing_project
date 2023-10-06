#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 2023

Functions to attach the LCFS to carbon emissions, based on code by Anne Owen

@author: lenakilian
"""

import pandas as pd


def import_lcfs(year, coicop_lookup, lcf_filepath):
    
    yr = str(year)
    
    dvhh_file = coicop_lookup.loc[coicop_lookup['Desc_full'] == 'dvhh', yr].tolist()[0]
    dvper_file = coicop_lookup.loc[coicop_lookup['Desc_full'] == 'dvper', yr].tolist()[0]
    
    dvhh = pd.read_csv(lcf_filepath + dvhh_file, sep='\t')
    dvper = pd.read_csv(lcf_filepath + dvper_file, sep='\t')
    
    dvhh.columns = [x.lower() for x in dvhh.columns]
    dvper.columns = [x.lower() for x in dvper.columns]
    
    dvhh = dvhh.set_index('case')
    dvper = dvper.set_index(['case', 'person'])
    
    # import person data
    dvper_lookup = coicop_lookup.loc[coicop_lookup['Dataset'] == 'dvper'].set_index('Desc_full')
    
    person_data = pd.DataFrame(index=dvper.index)
    for item in dvper_lookup.index.tolist():
        var = dvper_lookup.loc[item, yr]
        if var == 0:
            person_data[item] = 0
        else:
            person_data[item] = dvper[var]
    person_data = person_data.apply(lambda x: pd.to_numeric(x, errors='coerce'))
    person_data['no_people'] = 1
    # edit gender so they get added as list in one column - to keep individual information
    person_data['gender_all'] = person_data['gender_all'].fillna(0).map({1:'M', 2:'W', 0:'NA'})
    person_data['gender_age_all'] = person_data['gender_all'] + '_' + person_data['age_all'].astype(str) # make variable combining gender and age
    # make list vars
    person_data['gender_all'] = [[x] for x in person_data['gender_all']] 
    person_data['gender_age_all'] = [[x] for x in person_data['gender_age_all']] 
    # edit ages so they get added as list in one column - to keep individual ages, rather than get sum of all ages
    person_data['age_all'] = [[x] for x in person_data['age_all']] 
    # get sum
    person_data = person_data.sum(axis=0, level='case', skipna=True)
    # code is 0 if no partners or spouses in household. Therefore can make a binary, making all with sum 0 False (0) and all with sum >0 True (1)
    person_data.loc[person_data['partners_spouses'] > 0, 'partners_spouses'] = 1
    # sort gender_all and age_all alphabetically to more easily compare between households
    new_age = []; new_gender = []
    for i in range(len(person_data)):
        gender = sorted(person_data['gender_all'].iloc[i]); new_gender.append(gender)
        age = sorted(person_data['age_all'].iloc[i]); new_age.append(age)
    person_data['gender_all'] = new_gender
    person_data['age_all'] = new_age
    # extract lowest and highest ages
    person_data['age_youngest'] = [x[0] for x in person_data['age_all']]
    person_data['age_oldest'] = [x[-1] for x in person_data['age_all']]
    
    # import househols data
    dvhh_lookup = coicop_lookup.loc[coicop_lookup['Dataset'] == 'dvhh'].set_index('Coicop_full')
    
    useful_data = pd.DataFrame(index=dvhh.index)

    exp_items = [] # collect these to multiply by weight later
    for item in dvhh_lookup.index.tolist():
        if item[0] == '0':
            desc = dvhh_lookup.loc[item, 'Desc_full']
        else:
            desc = item
            exp_items.append(desc)
        
        var = dvhh_lookup.loc[item, yr]
        if var == 0 or var == '0':
            useful_data[desc] = 0
        elif var[:3] == '(-)':
            useful_data[desc] = -1*dvhh[var[3:].lower()]
        else:
            useful_data[desc] = dvhh[var.lower()]
    
    # rename dwelling types
    #dwelling_dict = {0:'Not recorded', 1:'Whole house bungalow-detached', 2:'Whole house bungalow semi-detached', 
    #                 3:'Whole house bungalow terrace', 4:'Purpose built flat maisonette', 5:'Part of house converted flat', 6:'Others'}
    dwelling_dict = {0:'Not recorded', 1:'Detached house', 2:'Semi-detached or terrace house', 
                     3:'Semi-detached or terrace house', 4:'Apartment', 5:'Apartment', 6:'Other'}
    useful_data['category of dwelling'] = useful_data['category of dwelling'].fillna(0).map(dwelling_dict)
    
    # multiply expenditure variables by weight to get UK total
    useful_data[exp_items] = useful_data[exp_items].apply(lambda x: x * useful_data['weight'])
    
    # combine person and household data
    useful_data = person_data.join(useful_data)
    
    # fix imputed rent by using home ownership (values 5, 6, 7 indicate home ownership)
    useful_data.loc[useful_data['home_ownership'].isin([5, 6, 7]) == False, 'home_ownership'] = 0
    useful_data.loc[useful_data['home_ownership'].isin([5, 6, 7]) == True, 'home_ownership'] = 1
    
    useful_data['4.2.1.1.1'] = useful_data['4.2.1.1.1'] * useful_data['home_ownership']
    
   
    return useful_data

