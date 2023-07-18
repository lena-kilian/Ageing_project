#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import estimate_emissions_main_function as estimate_emissions
from sys import platform
import pathlib

# set working directory
# make different path depending on operating system

path = str(pathlib.Path().resolve())

if platform[:3] == 'win' and 'ds.leeds.ac.uk' in path:
    data_path = 'O:/UKMRIO_Data/data/model_inputs/'
elif platform[:3] == 'win' and 'ds.leeds.ac.uk' not in path:
    data_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'
else:
    data_path = r'/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/UKMRIO_Data/'

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2017, 2020))

# load LFC data
lcfs = {year: pd.read_csv(output_path + 'outputs/LCFS/hhdspend_' + str(year) + '.csv', index_col=0) for year in years}
people = {}; hhdspend={}
for year in years:
    people[year] = lcfs[year].loc[:,:'1.1.1.1.1'].iloc[:,:-1]
    hhdspend[year] = lcfs[year].loc[:,'1.1.1.1.1':'12.7.1.1.6'].astype(float).apply(lambda x: x*lcfs[year]['weight'])
    
hhd_ghg, multipliers = estimate_emissions.make_footprint(hhdspend, data_path)




## Requirements: Run ukmrio_main_2023.py and LCFS_data_main_2023.py and sub_national_footprints_2023_main.py first
"""
import LCF_functions as lcf
import demand_functions as dm
import defra_functions as defra
import ukmrio_functions as uk

concs_dict = pd.read_excel(os.path.join(inputs_filepath, 'ONS_to_COICOP_LCF_concs.xlsx'), sheet_name=None, header = (0), index_col=0)

Y2 = lcf.convert43to41(Y, concs_dict, allyears)

Y=Y2

total_Yhh_109 = dm.make_Yhh_109_34(Y, years, meta)

coicop_exp_tot = lcf.make_totals_2023(hhspenddata, years)

coicop_exp_tot2 = lcf.convert_exp_tot_sizes(coicop_exp_tot, concs_dict, years, '456_to_109')

coicop_exp_tot3 = lcf.make_balanced_totals_2023(coicop_exp_tot2, total_Yhh_109, concs_dict, years) # cannot multiply because it is 109 instead of 112 columns

yhh_wide = lcf.make_y_hh_109(Y, coicop_exp_tot3, years, concs_dict, meta)
    
newY = lcf.make_new_Y_109(Y, yhh_wide, years)
"""
