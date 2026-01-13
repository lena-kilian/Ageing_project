#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import copy as cp
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# set working directory
# make different path depending on operating system

output_path = 'O:/geolki/Ageing/'
plot_path = 'C:/Users/geolki/OneDrive - Universiteit Leiden/Projects/2023_Ageing project/analysis/'

years = [2019]

width_scale = 0.4
space = 0.2


plot_cols = ['#E1812C', '#3274A1']

results = {}; expenditure = {}; count = {}
for year in years:
    results[year] = pd.read_excel(output_path + 'outputs/CO2_by_hhds.xlsx', sheet_name=str(year), index_col='case')
    expenditure[year] = pd.read_excel(output_path + 'outputs/EXP_by_hhds.xlsx', sheet_name=str(year), index_col='case')
    count[year] = results[year].groupby(['household_comp', 'age_group']).count()[['GOR']]

pop = 'no_people' # 'OECD scale' #

# keep only categories linked to fuel burning in home; electricity; personal travel
cat_dict = {'4.5.1 Electricity':'Electricity', '4.5.2 Gas':'Gas', 
            '4.5.3 Liquid fuels':'Other home energy', '4.5.4 Solid fuels':'Other home energy', '4.5.5 Heat energy':'Other home energy'}

cats_co2 = []
for item in list(cat_dict.values()):
    if item not in cats_co2:
        cats_co2.append(item)
        
cats_spend = ['Spend_' + x for x in cats_co2]

person_cols = results[list(results.keys())[0]].loc[:,:'OECD scale'].columns.tolist()

for item in results[list(results.keys())[0]].columns:
    if item not in person_cols and item not in list(cat_dict.keys()):
        cat_dict[item] = 'Other_co2'
        
# aggregate emission products

order_groups = ['single younger', 'single 65+', 'single 75+', 'couple younger', 'couple 65+', 'couple 75+', 'other younger', 'other 65+', 'other 75+']
order_hhld_comp = ['single', 'couple', 'other']
order_age = ['younger', '65+', '75+']

for year in years:
    results[year] = results[year].rename(columns=cat_dict).sum(axis=1, level=0)
    expenditure[year] = expenditure[year].rename(columns=cat_dict).fillna(0).sum(axis=1, level=0)
    expenditure[year].columns = ['Spend_' + x for x in expenditure[year].columns.tolist()]
    
    results[year] = results[year].join(expenditure[year])
    
    results[year]['hhd_comp_X_age'] = results[year]['household_comp'] + ' ' + results[year]['age_group']
    results[year]['hhd_comp_X_age'] = pd.Categorical(results[year]['hhd_comp_X_age'], categories=order_groups, ordered=True)
    results[year]['household_comp'] = pd.Categorical(results[year]['household_comp'], categories=order_hhld_comp, ordered=True)
    results[year]['age_group'] = pd.Categorical(results[year]['age_group'], categories=order_age, ordered=True)
    results[year]['age_hrp'] = pd.Categorical(results[year]['age_hrp'], categories=order_age, ordered=True)
    
    if 'Other_co2' in results[year].columns.tolist():
        results[year] = results[year].drop('Other_co2', axis=1)
    
results_all = pd.DataFrame()
for year in years:
    temp = cp.copy(results[year])
    temp['year'] = year
    results_all = results_all.append(temp)
    

survey_count = results_all.groupby(['hhd_comp_X_age', 'year']).count()[['GOR']]

check = results_all.groupby(['hhd_comp_X_age', 'year']).describe()\
    .swaplevel(axis=1)[['mean', 'min', 'max', 'count']]\
        .swaplevel(axis=1)[['age_youngest', 'age_oldest', 'Electricity', 'Gas', 'no_people']]
        
check2 = results_all.set_index(['hhd_comp_X_age', 'year'])
check2['age_all'] = check2['age_all'].str.replace('[', '').str.replace(']', '').str.split(', ')
check2 = pd.DataFrame(check2['age_all'].tolist(), index=check2.index).stack().reset_index().drop('level_2', axis=1)
check2[0] = check2[0].astype(int)
check2 = check2.loc[check2[0] >= 18]
check2 = check2.groupby(['hhd_comp_X_age', 'year']).mean() 

results_all['domestic_energy_co2'] = results_all[cats_co2].sum(1)
results_all['domestic_energy_spend'] = results_all[cats_spend].sum(1)

keep = ['hhd_comp_X_age', 'weight', 'no_people', 'Income anonymised',  'rooms in accommodation', 'domestic_energy_co2', 'domestic_energy_spend']


# Combined composition 
means_uk = cp.copy(results_all)[keep]
means_uk['pop'] = means_uk['no_people'] * means_uk['weight']
means_uk[['domestic_energy_co2', 'domestic_energy_spend']] = means_uk[['domestic_energy_co2', 'domestic_energy_spend']].apply(lambda x: x*means_uk['weight'])
means_uk = means_uk.groupby(['hhd_comp_X_age']).sum()
means_uk[['domestic_energy_co2', 'domestic_energy_spend']] = means_uk[['domestic_energy_co2', 'domestic_energy_spend']].apply(lambda x: x/means_uk['pop'])

temp = cp.copy(results_all)[keep]
temp['pop'] = temp['no_people'] * temp['weight']
temp[['rooms in accommodation']] = temp[['rooms in accommodation']].apply(lambda x: x*temp['weight'])
temp = temp.groupby(['hhd_comp_X_age']).sum()
temp['dwelling_size'] = temp['rooms in accommodation']/temp['pop']

means_uk = means_uk[['domestic_energy_co2', 'domestic_energy_spend']].join(temp[['dwelling_size']])
means_uk['Country'] = 'UK'

# import Japan data
data_jp = pd.read_excel(plot_path + 'outputs/ghg_by_hhd_types_202501_Japan_CLEAN.xlsx', sheet_name=None)
jp_energy = data_jp['dom_energy_CO2'].set_index(['Unnamed: 0'])
jp_energy.columns = ['domestic_energy_co2', 'CO2_se', 'CO2_95_1', 'CO2_95_2']

temp = data_jp['dom_energy_spend'].set_index(['Unnamed: 0'])
temp.columns = ['domestic_energy_spend', 'spend_se', 'spend_95_1', 'spend_95_2']

jp_energy = jp_energy.join(temp)

temp = data_jp['house_size'].set_index(['Unnamed: 0'])
temp.columns = ['dwelling_size', 'dwelling_se', 'dwelling_95_1', 'dwelling_95_2']

means_jp = jp_energy.join(temp)
means_jp['Country'] = 'Japan'

# combine
means_all = means_uk.append(means_jp).reset_index().rename(columns={'index':'hhld_comp'})
means_all['hhld_comp'] = means_all['hhld_comp'].str.replace('_young', ' younger').str.replace('_', ' ').str.title()
means_all['hhld_comp'] = pd.Categorical(means_all['hhld_comp'], categories=[x.title() for x in order_groups], ordered=True)


# Individual composition
means_uk = pd.DataFrame()
for item in ['age_group', 'household_comp']:
    temp = cp.copy(results_all)[keep + [item]]
    temp['pop'] = temp['no_people'] * temp['weight']
    temp[['domestic_energy_co2', 'domestic_energy_spend']] = temp[['domestic_energy_co2', 'domestic_energy_spend']].apply(lambda x: x*temp['weight'])
    temp = temp.groupby([item]).sum()
    temp[['domestic_energy_co2', 'domestic_energy_spend']] = temp[['domestic_energy_co2', 'domestic_energy_spend']].apply(lambda x: x/temp['pop'])
    temp['split'] = item
    
    temp2 = cp.copy(results_all)[keep + [item]]
    temp2['pop'] = temp2['no_people'] * temp2['weight']
    temp2[['rooms in accommodation']] = temp2[['rooms in accommodation']].apply(lambda x: x*temp2['weight'])
    temp2 = temp2.groupby([item]).sum()
    temp2['dwelling_size'] = temp2['rooms in accommodation']/temp2['pop']
    
    temp = temp.join(temp2[['dwelling_size']])
    temp = temp.reset_index().rename(columns={item:'group'})
    temp2['split'] = item
    
    means_uk = means_uk.append(temp)

means_uk['Country'] = 'UK'

# import Japan data
means_jp = data_jp['means_groups']
means_jp['Country'] = 'Japan'

# combine

keep2 = ['Country', 'group', 'split', 'domestic_energy_co2', 'domestic_energy_spend']
means_split = means_uk[keep2].append(means_jp[keep2])
means_split['group'] = means_split['group'].str.replace('young', 'younger').str.replace('youngerer', 'younger').str.title()

#################
## Single Axis ## 
#################

# single axis 
# CO2 combined composition
sns.barplot(data=means_all.reset_index(), x='hhld_comp', y='domestic_energy_co2', hue='Country', palette=sns.color_palette(plot_cols))
plt.xticks(rotation=90); plt.xlabel('');
plt.ylabel('Domestic Emissions per Capita (tCO2/capita)')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_co2.png', dpi=200, bbox_inches='tight'); plt.show()

# CO2 split composition
plot_data = means_split[['Country', 'group', 'split', 'domestic_energy_co2']]
fig, axs = plt.subplots(ncols=2, figsize=(10, 5))
for i in range(2):
    split = plot_data['split'].unique()[i]
    temp = plot_data.loc[plot_data['split'] == split].sort_values('Country')
    
    if split == 'household_comp' :  
        temp['group'] = pd.Categorical(temp['group'], categories=['Single', 'Couple', 'Other'], ordered=True)
    else:
        temp['group'] = pd.Categorical(temp['group'], categories=['Younger', '65+', '75+'], ordered=True)
    
    sns.barplot(ax=axs[i], data=temp, x='group', y='domestic_energy_co2', hue='Country', palette=sns.color_palette(plot_cols))
    axs[i].set_ylabel('Domestic Emissions per Capita (tCO2/capita)')  
axs[0].set_xlabel('Age Group');
axs[1].set_xlabel('Household Composition');
axs[0].get_legend().remove()
legend_patches = []
legend_patches.append(mpatches.Patch(color=plot_cols[0], label='Japan'))
legend_patches.append(mpatches.Patch(color=plot_cols[1], label='UK'))
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, title='Country', handles=legend_patches)
axs[1].set_ylabel('')
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_co2_split.png', dpi=200, bbox_inches='tight'); plt.show()


# Income 
income_groups = list(range(0, 100, 15))
uk_dict = {}
temp = cp.copy(results_all[keep])
temp['Income anonymised'] = temp['Income anonymised'] * (365.25/7) / 1000
temp['Income'] = 'more than ' + str(income_groups[-1])
temp['Income Group'] = 6
for i in range(len(income_groups[:-1])):
    temp.loc[(temp['Income anonymised'] >= income_groups[i]) & (temp['Income anonymised'] < income_groups[i+1]), 'Income'] = str(income_groups[i]) + '-' +  str(income_groups[i+1])
    temp.loc[(temp['Income'] == str(income_groups[i]) + '-' +  str(income_groups[i+1])), 'Income Group'] = i
    uk_dict[i] = str(income_groups[i]) + '-' +  str(income_groups[i+1])
uk_dict[0] = 'less than 15'
uk_dict[6] = 'more than 90'
temp = temp.groupby(['hhd_comp_X_age', 'Income Group']).sum()[['weight']].unstack(['hhd_comp_X_age']).droplevel(axis=1, level=0)
temp = temp.apply(lambda x: x/x.sum() * 100).cumsum(axis=0)
temp = pd.DataFrame(temp.stack()).rename(columns={0:'Percent'}).reset_index(level=0)
temp['Country'] = 'UK'
temp.index = [x.replace('_young', ' younger').replace('_', ' ').title() for x in temp.index]

jp_dict = {'less than 2.5':0, '2.5-5':1, '5-7.5':2, '7.5-10':3, '10-15':4, '15-20':5, 'more than 20':6, 'unkown':np.nan}
means_scaled = data_jp['hhld_income'].set_index('Unnamed: 0').drop('Cum.', axis=1)
means_scaled.columns = ['Income', 'Percent']
means_scaled['Income'] = means_scaled['Income'].str.replace(' ', '').str.replace('than', ' than ')
means_scaled['Income Group'] = means_scaled['Income'].map(jp_dict)
jp_dict = means_scaled[['Income Group', 'Income']].drop_duplicates()
jp_dict['Income'] = jp_dict['Income'] + '.0'
jp_dict['Income'] = jp_dict['Income'].str.replace('-', '.0-').str.replace('2.5.0', '2.5').str.replace('7.5.0', '7.5')
jp_dict = dict(zip(jp_dict['Income Group'], jp_dict['Income']))
means_scaled = means_scaled.set_index('Income Group', append=True).drop('Income', axis=1).unstack('Unnamed: 0').fillna(0).drop(np.nan, axis=0)
means_scaled = means_scaled.apply(lambda x: x/x.sum() * 100).cumsum(axis=0)
means_scaled = pd.DataFrame(means_scaled.stack()).reset_index(level=0)
means_scaled['Country'] = 'Japan'
means_scaled.index = [x.replace('_young', ' younger').replace('_', ' ').title().replace(' C', 'C').replace(' S', 'S').replace(' O', 'O') for x in means_scaled.index]

means_scaled = means_scaled.append(temp).reset_index().rename(columns={'index':'hhld_comp'})
means_scaled['hhld_comp'] = pd.Categorical(means_scaled['hhld_comp'], categories=[x.title() for x in order_groups], ordered=True)

means_scaled['Income Group'] = (means_scaled['Income Group'].astype(int) + 1).astype(str)

# 'coolwarm', 'PRGn'
fig, axs = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(8, 8))
# Japan
temp = means_scaled.loc[means_scaled['Country'] == 'Japan'].sort_values('Income Group', ascending=False)
temp['Income'] = (temp['Income Group'].astype(int) - 1).map(jp_dict)
sns.barplot(ax=axs[0], data=temp, y='hhld_comp', x='Percent', hue='Income', palette='PRGn', dodge=False)
axs[0].legend(bbox_to_anchor=(1,1), title='Japan Income\n(million Yen)')
axs[0].set_ylabel('Japan Households')     
axs[0].axhline(2.5, c='k', linestyle=':'); axs[0].axhline(5.5, c='k', linestyle=':'); 

# UK
temp = means_scaled.loc[means_scaled['Country'] == 'UK'].sort_values('Income Group', ascending=False)
temp['Income'] = (temp['Income Group'].astype(int) - 1).map(uk_dict)
sns.barplot(ax=axs[1], data=temp, y='hhld_comp', x='Percent', hue='Income', palette='coolwarm', dodge=False)
axs[1].legend(bbox_to_anchor=(1,1), title='UK income\n(thousand GBP)')

axs[1].set_ylabel('UK Households')
axs[1].axhline(2.5, c='k', linestyle=':'); axs[1].axhline(5.5, c='k', linestyle=':'); 

axs[1].set_xlabel('Percentage of Households (%)')
axs[0].set_xlabel('')
plt.xlim(0, 100)
plt.savefig(plot_path + 'outputs/plots/income_uk_jp_group_sep2.png', dpi=200, bbox_inches='tight'); plt.show()

###############
## Dual plot ## 
###############

# Spend
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['domestic_energy_spend'].unstack('Country').reset_index()

fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(12, 5))
legend_patches = []

sns.barplot(ax=axs[0], data=means_scaled.reset_index(), x='hhld_comp', y='Japan', color=plot_cols[0])
sns.barplot(ax=axs[1], data=means_scaled.reset_index(), x='hhld_comp', y='UK', color=plot_cols[1])

axs[0].set_ylabel('Japan Domestic Energy Spend per Capita (Yen/capita)'); 
axs[1].set_ylabel('UK Domestic Energy Spend per Capita (GBP/capita)')
axs[0].set_title('Japan')
axs[1].set_title('UK')

for i in range(2):
    axs[i].set_xlabel('')
    axs[i].axvline(2.5, c='k', linestyle=':');
    axs[i].axvline(5.5, c='k', linestyle=':'); 
    axs[i].tick_params(axis='x', labelrotation=90); 

plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_spend_dual.png', dpi=200, bbox_inches='tight'); plt.show()



# Dwelling

means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['dwelling_size'].unstack('Country').reset_index()

fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(12, 5))
legend_patches = []

sns.barplot(ax=axs[0], data=means_scaled.reset_index(), x='hhld_comp', y='Japan', color=plot_cols[0])
sns.barplot(ax=axs[1], data=means_scaled.reset_index(), x='hhld_comp', y='UK', color=plot_cols[1])

axs[0].set_ylabel('Japan Area of Dwelling per Capita (m2/capita)'); 
axs[1].set_ylabel('UK Number of Rooms in Dwelling per Capita')
axs[0].set_title('Japan')
axs[1].set_title('UK')

for i in range(2):
    axs[i].set_xlabel('')
    axs[i].axvline(2.5, c='k', linestyle=':');
    axs[i].axvline(5.5, c='k', linestyle=':'); 
    axs[i].tick_params(axis='x', labelrotation=90); 

plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_dwelling_dual.png', dpi=200, bbox_inches='tight'); plt.show()


###############
## Twin Axis ## 
###############

# Spend
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['domestic_energy_spend'].unstack('Country').reset_index()

fig, ax = plt.subplots(sharex=True)
legend_patches = []

sns.barplot(ax=ax, data=means_scaled.reset_index(), x='hhld_comp', y='Japan', color=plot_cols[0])

for bar in ax.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + space/2)
    bar.set_width(bar.get_width() * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[0], label='Japan'))
ax.set_ylabel('Japan Domestic Energy Spend per Capita (Yen/capita)')

ax2 = ax.twinx()
sns.barplot(ax=ax2,  data=means_scaled.reset_index(), x='hhld_comp', y='UK', color=plot_cols[1])
for bar in ax2.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + w * (1- width_scale) - space/2)
    bar.set_width(w * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[1], label='UK'))
ax2.set_ylabel('UK Domestic Energy Spend per Capita (GBP/capita)')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, title='Country', handles=legend_patches)

ax.tick_params(axis='x', labelrotation=90); ax.set_xlabel('');
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_spend_twin.png', dpi=200, bbox_inches='tight'); plt.show()


# Dwelling
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['dwelling_size'].unstack('Country').reset_index()

fig, ax = plt.subplots(sharex=True)
legend_patches = []
sns.barplot(ax=ax, data=means_scaled.reset_index(), x='hhld_comp', y='Japan', color=plot_cols[0])

for bar in ax.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + space/2)
    bar.set_width(bar.get_width() * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[0], label='Japan'))
ax.set_ylabel('Japan Area of Dwelling per Capita (m2/capita)')

ax2 = ax.twinx()
sns.barplot(ax=ax2,  data=means_scaled.reset_index(), x='hhld_comp', y='UK', color=plot_cols[1])
for bar in ax2.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + w * (1- width_scale) - + space/2)
    bar.set_width(w * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[1], label='UK'))
ax2.set_ylabel('UK Number of Rooms in Dwelling per Capita')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, title='Country', handles=legend_patches)
ax.tick_params(axis='x', labelrotation=90); ax.set_xlabel('');
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_dwelling_twin.png', dpi=200, bbox_inches='tight'); plt.show()



# for SI by composition split
width_scale = 0.375
for i in range(2):
    fig, ax = plt.subplots(sharex=True, figsize=(5, 5))
    legend_patches = []

    plot_data = means_split[['Country', 'group', 'split', 'domestic_energy_spend']]
    split = plot_data['split'].unique()[i]
    temp = plot_data.loc[plot_data['split'] == split].sort_values('Country')
    
    if i == 1:    
        temp['group'] = pd.Categorical(temp['group'], categories=['Single', 'Couple', 'Other'], ordered=True)
    if i == 0:
        temp['group'] = pd.Categorical(temp['group'], categories=['Younger', '65+', '75+'], ordered=True)
    
    temp_jp = temp.loc[temp['Country'] == 'Japan']
    sns.barplot(ax=ax, data=temp_jp, x='group', y='domestic_energy_spend', color=plot_cols[0])
    for bar in ax.containers[0]:
        x = bar.get_x()
        w = bar.get_width()
        bar.set_x(x + space/2)
        bar.set_width(bar.get_width() * width_scale)
    legend_patches.append(mpatches.Patch(color=plot_cols[0], label='Japan'))
    ax.set_ylabel('Japan Domestic Energy Spend per Capita (Yen/capita)')
    
    temp_uk = temp.loc[temp['Country'] == 'UK']
    ax2 = ax.twinx()
    sns.barplot(ax=ax2,  data=temp_uk, x='group', y='domestic_energy_spend', color=plot_cols[1])
    for bar in ax2.containers[0]:
        x = bar.get_x()
        w = bar.get_width()
        bar.set_x(x + w * (1- width_scale) - space/2)
        bar.set_width(w * width_scale)
    legend_patches.append(mpatches.Patch(color=plot_cols[1], label='UK'))
    ax2.set_ylabel('UK Domestic Energy Spend per Capita (GBP/capita)')
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, title='Country', handles=legend_patches)
    
    ax.set_xlabel(['Age Group', 'Household Composition'][i]);
    plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_spend_twin_split_' + split + '.png', dpi=200, bbox_inches='tight'); plt.show()
    


