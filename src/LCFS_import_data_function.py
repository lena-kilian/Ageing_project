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
    person_data['no_people'] = 1
    person_data = person_data.apply(lambda x: pd.to_numeric(x, errors='coerce')).sum(axis=0, level='case', skipna=True)
        
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
        elif var[0] == '-':
            useful_data[desc] = -1*dvhh[var[1:]]
        else:
            useful_data[desc] = dvhh[var]
    
    # multiply expenditure variables by weight to get UK total
    useful_data[exp_items] = useful_data[exp_items].apply(lambda x: x * useful_data['weight'])
    
    # combine person and household data
    useful_data = person_data.join(useful_data)
    
    # fix imputed rent by using home ownership (values 5, 6, 7 indicate home ownership)
    useful_data.loc[useful_data['home_ownership'].isin([5, 6, 7]) == False, 'home_ownership'] = 0
    useful_data.loc[useful_data['home_ownership'].isin([5, 6, 7]) == True, 'home_ownership'] = 1
    
    useful_data['4.2.1.1.1'] = useful_data['4.2.1.1.1'] * useful_data['home_ownership']
   
    return useful_data

