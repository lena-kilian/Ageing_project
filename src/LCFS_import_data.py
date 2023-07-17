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

years = list(range(2001, 2021))

# Load LCFS data
coicop_lookup = pd.read_csv(output_path + 'inputs/LCF_variables.csv', header = 0).fillna(0)

lcfs = {year: lcfs_import.import_lcfs(year, coicop_lookup, data_path + 'raw/LCFS/') for year in years}


# age_dict = {0:'Not recorded', 3:'15-19', 4:'20-25', 5:'25-30' , 6:'30-35', 7:'35-40', 8:'40-45', 9:'45-50', 10:'50-55', 11:'55-60', 
#             12:'60-65', 13:'65-70', 14:'70-75', 15:'75-80', 16:'80+'}


# single = pd.DataFrame(index=list(age_dict.keys()))
# for year in years:
#     temp = lcfs[year]
#     temp = temp.loc[temp['no people'] == 1]
#     temp = temp.groupby(['age of household reference person by range - anonymised']).count()[['weight']]
#     temp.columns = [year]
#     single = single.join(temp).fillna(0)
    
# single = single.rename(index=age_dict)


single = pd.DataFrame(index=['60+', '65+', '69+'])
for year in years:
    temp = lcfs[year]
    temp = temp.loc[(temp['no people'] == 1)]
    temp['65+'] = temp[['people aged 65-69', 'people aged >69']].sum(1)
    keep = []
    for ages in [['people aged 60-64', 'people aged 65-69', 'people aged >69'], ['people aged 65-69', 'people aged >69'], ['people aged >69']]:
        name = ages[0].split('aged ')[-1].replace('>', '')[:2] + '+'
        temp[name] = temp[ages].sum(1)
        temp.loc[temp[name] == 1, name] = True
        temp.loc[temp[name] != True, name] = False
        keep.append(name)
    temp = pd.DataFrame(temp[keep].stack()).reset_index()
    temp = temp.groupby(['level_1', 0]).count().reset_index()
    temp = temp.loc[temp[0] == True].set_index('level_1')[['case']]
    temp.columns = [year]
    single = single.join(temp)


couple = pd.DataFrame(index=['60+', '65+', '69+'])
for year in years:
    temp = lcfs[year]
    temp = temp.loc[(temp['no people'] == 2) & (temp['partner_hhld'] == 1)]
    temp['65+'] = temp[['people aged 65-69', 'people aged >69']].sum(1)
    keep = []
    for ages in [['people aged 60-64', 'people aged 65-69', 'people aged >69'], ['people aged 65-69', 'people aged >69'], ['people aged >69']]:
        name = ages[0].split('aged ')[-1].replace('>', '')[:2] + '+'
        temp[name] = temp[ages].sum(1)
        temp.loc[temp[name] == 2, name] = True
        temp.loc[temp[name] != True, name] = False
        keep.append(name)
    temp = pd.DataFrame(temp[keep].stack()).reset_index()
    temp = temp.groupby(['level_1', 0]).count().reset_index()
    temp = temp.loc[temp[0] == True].set_index('level_1')[['case']]
    temp.columns = [year]
    couple = couple.join(temp)

