# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 17:59:26 2023

@author: geolki
"""

import pandas as pd
import copy as cp
import matplotlib.pyplot as plt
import numpy as np

output_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

# load LFC data
ghg_data = pd.read_excel(output_path + 'outputs/GHG_by_hhds.xlsx', index_col=0, sheet_name=None)

fp_defs = ['10% & below median income', '10% only', 'LIHC']
fp_dict = dict(zip(fp_defs, 
                   ["(ghg_data[item]['energy_spend'] > ghg_data[item]['Income anonymised']/10) & (ghg_data[item]['Income anonymised'] < ghg_data[item]['Income anonymised'].median())",
                    "(ghg_data[item]['energy_spend'] > ghg_data[item]['Income anonymised']/10)",
                    "(ghg_data[item]['Income anonymised'] < ghg_data[item]['Income anonymised'].median()) & (ghg_data[item]['energy_spend'] > ghg_data[item]['energy_spend'].median())"
                    ]))

### deifnition 10% & below median income
results = {}
for fp in fp_defs:
    results[fp] = pd.DataFrame()
    for item in list(ghg_data.keys()):
        ghg_data[item]['energy_spend'] = ghg_data[item].loc[:, 'spend_4.5.1_Combined electricity meter payment less rebate':
                                                            'spend_4.5.5_Hot water, steam and ice'].sum(1)
        ghg_data[item]['fuel_poor'] = False
        ghg_data[item].loc[eval(fp_dict[fp]), 'fuel_poor'] = True
        
        temp = cp.copy(ghg_data[item])
        temp.loc[temp['hhd_type_1_gender'].isna() == True, 'hhd_type_1_gender'] = 'Other'
        temp = temp.fillna(0).sort_values(['hhd_type', 'fuel_poor', 'hhd_type_1_gender']).set_index(['hhd_type', 'fuel_poor', 'hhd_type_1_gender'])
        temp['pop_scaled'] =  temp['weight']*temp['OECD scale']
        temp.loc[:,'1.1.1 Bread and cereals':'12.7.1 Other services n.e.c.'] = temp.loc[:,'1.1.1 Bread and cereals':'12.7.1 Other services n.e.c.'].apply(lambda x:x*temp['weight'])
        temp = temp.sum(axis=0, level=[0, 1, 2])
        cols = temp.loc[:,'1.1.1 Bread and cereals':'12.7.1 Other services n.e.c.'].columns.tolist()
        temp[cols] = temp[cols].apply(lambda x:x/temp['pop_scaled'])
        temp = temp[['pop_scaled'] + cols]
        temp.columns = [x.split('.')[0] for x in temp.columns]
        temp = temp.sum(axis=1, level=0)
        temp['year'] = int(item)
        
        results[fp] = results[fp].append(temp)

for fp in fp_defs:
    plot_data = results[fp].loc[results[fp]['year'] >= 2017]
    plot_data.loc[:,'1':'12'] = plot_data.loc[:,'1':'12'].apply(lambda x:x*plot_data['pop_scaled'])
    plot_data = plot_data.sum(axis=0, level=[0, 1, 2])
    plot_data = plot_data.loc[:,'1':'12'].apply(lambda x:x/plot_data['pop_scaled']).reset_index()
    plot_data.loc[plot_data['hhd_type_1_gender'] == 'Other', 'hhd_type_1_gender'] = ''
    plot_data['hhd_type'] = plot_data['hhd_type'] + '_' + plot_data['hhd_type_1_gender']
    plot_data = plot_data.drop(['hhd_type_1_gender'], axis=1).sort_values(['hhd_type', 'fuel_poor'])
    
    plot_data.set_index(['hhd_type', 'fuel_poor']).plot(kind='bar', stacked=True)
    plt.legend(bbox_to_anchor=(1,1))
    plt.title(fp)
    for i in range(7):
        plt.axvline(x=i*2 - 0.5, c='k')
    plt.ylim(0, 16)
    plt.savefig(output_path + 'outputs/plots/2017-2019_' + fp + '.png', bbox_inches='tight', dpi=200)
    
demographics = {} 
for fp in fp_defs:
    demographics[fp] = pd.DataFrame()
    for yr in range(2007, 2020):
        item = str(yr)
        ghg_data[item]['energy_spend'] = ghg_data[item].loc[:, 'spend_4.5.1_Combined electricity meter payment less rebate':
                                                            'spend_4.5.5_Hot water, steam and ice'].sum(1)
        ghg_data[item]['fuel_poor'] = False
        ghg_data[item].loc[eval(fp_dict[fp]), 'fuel_poor'] = True
        
        temp = cp.copy(ghg_data[item])
        temp.loc[temp['hhd_type_1_gender'].isna() == True, 'hhd_type_1_gender'] = 'Other'
        temp = temp.fillna(0).sort_values(['hhd_type', 'fuel_poor', 'hhd_type_1_gender']).set_index(['hhd_type', 'fuel_poor', 'hhd_type_1_gender'])
        temp['age_all'] = temp['age_all'].str.replace('nan', 'np.nan')
        temp['age_mean'] = [sum(eval(x))/len(eval(x)) for x in temp['age_all']]
        
        mean_w = cp.copy(temp)
        vars_mean_w = ['Income anonymised', 'income tax', 'energy_spend']
        mean_w[vars_mean_w] = mean_w[vars_mean_w].apply(lambda x: x*mean_w['weight']*mean_w['no_people'])
        mean_w = mean_w.sum(axis=0, level=[0, 1, 2])
        mean_w = mean_w[vars_mean_w].apply(lambda x: x/(mean_w['weight'] * mean_w['OECD scale']))
        
        mean = cp.copy(temp)
        vars_mean = ['age_mean', 'rooms in accommodation']
        mean[vars_mean] = mean[vars_mean].apply(lambda x: x*mean['weight'])
        mean = mean.sum(axis=0, level=[0, 1, 2])
        mean = mean[vars_mean].apply(lambda x: x/(mean['weight']))
        
        count = cp.copy(temp)
        vars_count = ['GOR', 'OA class 1', 'home_ownership', 'ethnicity hrp', 'ethnicity partner hrp']
        count = count[vars_count + ['weight']].reset_index()
        count['count'] = 1
        count_results = count.groupby(['hhd_type', 'fuel_poor', 'hhd_type_1_gender'])[['weight', 'count']].sum()
        count_results['pct_of_hhlds'] = count_results['weight'] / count_results['weight'].sum() *100
        count_results['pct_of_surveys'] = count_results['count'] / count_results['count'].sum() *100
        for var in vars_count:
            temp2 = cp.copy(count)
            temp[var] = temp[var].astype(str)
            temp2['count_' + var] = 1
            temp2 = temp2.groupby(['hhd_type', 'fuel_poor', 'hhd_type_1_gender', var])[['count_' + var, 'weight']].sum()
            temp2['count_' + var] = temp2['count_' + var] * temp2['weight']
            temp2 = temp2[['count_' + var]].unstack(var).fillna(0)
            totals = temp2.sum(axis=1)
            for col in temp2.columns:
                temp2[col] = temp2[col] / totals * 100
            
            count_results = count_results.join(temp2)

        temp = mean_w.join(mean).join(count_results)
        temp['year'] = int(item)
        
        demographics[fp] = demographics[fp].append(temp).fillna(0)
    
demographics_all = pd.DataFrame()
for fp in fp_defs:
    temp = cp.copy(demographics[fp])
    temp['FP_def'] = fp
    demographics_all = demographics_all.append(temp.reset_index())
    
demographics_all_filter = demographics_all.loc[demographics_all['year'] == 2019]\
    .set_index(['hhd_type', 'hhd_type_1_gender', 'fuel_poor', 'FP_def'])\
    .unstack(level='FP_def')[['Income anonymised', 'energy_spend', 'age_mean', 'rooms in accommodation', 
                              'pct_of_hhlds', 'pct_of_surveys']]
    
    