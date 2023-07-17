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
    data_path = r'/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/data'

years = list(range(2001, 2021))
lcf_years = dict(zip(years, ['2001-2002', '2002-2003', '2003-2004', '2004-2005', '2005-2006', '2006', '2007', '2008', '2009', 
                             '2010', '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018', '2018-2019', '2019-2020',
                             '2020-2021']))

# Define function needed
def isNaN(string):
    return string != string


# Load LCFS data
lcfs = {}
for year in years:
    dvhh_file = data_path + 'raw/LCFS/' + lcf_years[year] + '/tab/' + lcf_years[year] + '_dvhh_ukanon.tab'
    dvper_file = data_path + 'raw/LCFS/' + lcf_years[year] + '/tab/' + lcf_years[year] + '_dvper_ukanon.tab'
    
    lcfs[year] = lcfs_import.import_lcfs(year, dvhh_file, dvper_file).drop_duplicates()
    lcfs[year] = lcfs[year].reset_index()
    lcfs[year].columns = [x.lower() for x in lcfs[year].columns]
    lcfs[year] = lcfs[year].set_index('case')  
    

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

