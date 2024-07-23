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
    
    file_list = lcf_filepath + str(yr) + '/tab'
    temp = coicop_lookup.loc[coicop_lookup['Dataset'] == 'link'].set_index('Desc_full')
    files = {name: file_list + '/' + temp.loc[name, yr] for name in ['dvhh', 'dvper']}

    
    data = {}
    person_dict = {}; household_dict = {}
    for dataset in list(files.keys()):

        data[dataset] = pd.read_csv(files[dataset], sep='\t', index_col=None,  encoding='utf8')\
            .rename(columns={'case1':'case'})
        data[dataset].columns = [x.lower() for x in data[dataset].columns]
        
        if 'hh' in dataset:
            data[dataset] = data[dataset].set_index('case')
            
            # import household data
            lookup = coicop_lookup.loc[coicop_lookup['Dataset'] == dataset].set_index('Coicop_full')
            
            useful_data = pd.DataFrame(index=data[dataset].index)

            exp_items = [] # collect these to multiply by weight later
            for item in lookup.index.tolist():
                if item[0] == '0':
                    desc = lookup.loc[item, 'Desc_full']
                else:
                    desc = item
                    exp_items.append(desc)
                
                var = lookup.loc[item, yr]
                if var == 0 or var == '0':
                    useful_data[desc] = 0
                elif var[:3] == '(-)':
                    useful_data[desc] = -1*data[dataset][var[3:].lower()]
                else:
                    useful_data[desc] = data[dataset][var.lower()]
            
            household_dict[dataset] = useful_data
            
        else:
            data[dataset] = data[dataset].set_index(['case', 'person'])
    
            # import person data
            lookup = coicop_lookup.loc[coicop_lookup['Dataset'] == dataset].set_index('Desc_full')
        
            person_data = pd.DataFrame(index=data[dataset].index)
            for item in lookup.index.tolist():
                var = lookup.loc[item, yr]
                if var == 0:
                    person_data[item] = 0
                else:
                    person_data[item] = data[dataset][var]
            person_dict[dataset] = person_data
    
    # clean up person variables
    if len(person_dict.keys()) > 1:
        temp = list(person_dict.keys())
        person_data = person_dict[temp[0]]
        for item in temp[1:]:
            person_data = person_data.join(person_dict[item])
                                 
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
    person_data['age_youngest'] = [min(x) for x in person_data['age_all']]
    person_data['age_oldest'] = [max(x) for x in person_data['age_all']]
        
    # clean up household_variables
    if len(household_dict.keys()) > 1:
        temp = list(household_dict.keys())
        useful_data = household_dict[temp[0]]
        order = useful_data.columns.tolist()
        for item in temp[1:]:
            useful_data = useful_data.join(household_dict[item])
            order = household_dict[item].columns.tolist() + order
        useful_data = useful_data[order]
   
    # rename dwelling types
    #dwelling_dict = {0:'Not recorded', 1:'Whole house bungalow-detached', 2:'Whole house bungalow semi-detached', 
    #                 3:'Whole house bungalow terrace', 4:'Purpose built flat maisonette', 5:'Part of house converted flat', 6:'Others'}
    dwelling_dict = {0:'Other', 1:'Detached, semi-detached or terrace house', 2:'Detached, semi-detached or terrace house', 
                     3:'Detached, semi-detached or terrace house', 4:'Apartment', 5:'Apartment', 6:'Other'}
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

