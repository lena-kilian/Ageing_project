# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 17:59:26 2023

@author: geolki
"""

import pandas as pd
import estimate_emissions_main_function as estimate_emissions
from sys import platform
import pathlib
import copy as cp

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

years = list(range(2017, 2020))

# load LFC data
ghg_data = pd.read_excel(output_path + 'outputs/GHG_by_hhds.xlsx', index_col=0, sheet_name=None)




