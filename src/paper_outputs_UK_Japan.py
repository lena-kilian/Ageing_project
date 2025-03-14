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
plot_path = 'C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/'

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
data_jp = pd.read_excel('C:/Users/geolki/OneDrive - University of Leeds/Postdoc/Ageing_project/analysis/outputs/ghg_by_hhd_types_202501_Japan_CLEAN.xlsx', sheet_name=None)
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

#################
## Single Axis ## 
#################

# single axis 
# CO2
sns.barplot(data=means_all.reset_index(), x='hhld_comp', y='domestic_energy_co2', hue='Country', palette=sns.color_palette(plot_cols))
plt.xticks(rotation=90); plt.xlabel('');
plt.ylabel('Domestic Emissions per Capita (tCO2/capita)')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_co2.png', dpi=200, bbox_inches='tight'); plt.show()

# Spend
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])[['domestic_energy_spend']].unstack('Country')
means_scaled = means_scaled.apply(lambda x: x/x.max())
means_scaled = means_scaled.stack('Country').reset_index()
sns.barplot(data=means_scaled.reset_index(), x='hhld_comp', y='domestic_energy_spend', hue='Country', palette=sns.color_palette(plot_cols))
plt.xticks(rotation=90); plt.xlabel('');
plt.ylabel('Domestic Energy Spend per Capita Rescaled')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_spend_scaled.png', dpi=200, bbox_inches='tight'); plt.show()

# Dwelling size
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])[['dwelling_size']].unstack('Country')
means_scaled = means_scaled.apply(lambda x: x/x.max())
means_scaled = means_scaled.stack('Country').reset_index()
sns.barplot(data=means_scaled.reset_index(), x='hhld_comp', y='dwelling_size', hue='Country', palette=sns.color_palette(plot_cols))
plt.xticks(rotation=90); plt.xlabel('');
plt.ylabel('Dwelling Size per Capita Rescaled')
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_dwelling_scaled.png', dpi=200, bbox_inches='tight'); plt.show()


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





fig, ax = plt.subplots()
legend_uk = []; legend_jp = []

n_colors = 7
palettes = [sns.color_palette('coolwarm', n_colors),  # sns.diverging_palette(570, 740, l=50, n=n_colors, sep=1, center="light")
            sns.color_palette('PRGn', n_colors)] ##['viridis', ]

# Japan
temp = means_scaled.loc[means_scaled['Country'] == 'Japan'].sort_values('Income Group', ascending=False)
jp_cols = palettes[1]
for i in temp['Income Group'].unique():
    n = 7-int(i)
    temp2 = temp.loc[temp['Income Group'] == i]
    sns.barplot(ax=ax, data=temp2, x='hhld_comp', y='Percent', color=jp_cols[n])
    for bar in ax.containers[7-int(i)]:
        x = bar.get_x()
        w = bar.get_width()
        bar.set_x(x + space/2)
        bar.set_width(bar.get_width() * width_scale)
    legend_jp.append(mpatches.Patch(color=jp_cols[n], label=jp_dict[float(i)-1]))

# UK
temp = means_scaled.loc[means_scaled['Country'] == 'UK'].sort_values('Income Group', ascending=False)
uk_cols = palettes[0]
for i in temp['Income Group'].unique():
    n = 7-int(i)
    temp2 = temp.loc[temp['Income Group'] == i]
    sns.barplot(ax=ax, data=temp2, x='hhld_comp', y='Percent', color=uk_cols[n])
    for bar in ax.containers[14-int(i)]:
        x = bar.get_x()
        w = bar.get_width()
        bar.set_x(x + w * (1- width_scale) - space/2)
        bar.set_width(w * width_scale)
    legend_uk.append(mpatches.Patch(color=uk_cols[n], label=uk_dict[int(i)-1]))
 
ax2 = ax.twinx()
ax2.get_yaxis().set_visible(False)

ax.legend(bbox_to_anchor=(1,0.5), title='UK income (thousand GBP)', handles=legend_uk)
ax2.legend(bbox_to_anchor=(1,1.1), title='Japan Income (million Yen)', handles=legend_jp)
     
ax.tick_params(axis='x', labelrotation=90); ax.set_xlabel(''); ax.set_ylim(0, 100)
ax.set_ylabel('Percentage of Households (%)' );
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/income_uk_jp_group.png', dpi=200, bbox_inches='tight'); plt.show()


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
## Twin Axis ## 
###############

# Co2
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['domestic_energy_co2'].unstack('Country').reset_index()

fig, ax = plt.subplots(sharex=True)
legend_patches = []

sns.barplot(ax=ax, data=means_scaled.reset_index(), x='hhld_comp', y='Japan', color=plot_cols[0])

for bar in ax.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + space/2)
    bar.set_width(bar.get_width() * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[0], label='Japan'))
ax.set_ylabel('Japan Domestic Energy Emissions per Capita (tCO2/capita)')

ax2 = ax.twinx()
sns.barplot(ax=ax2,  data=means_scaled.reset_index(), x='hhld_comp', y='UK', color=plot_cols[1])
for bar in ax2.containers[0]:
    x = bar.get_x()
    w = bar.get_width()
    bar.set_x(x + w * (1- width_scale) - space/2)
    bar.set_width(w * width_scale)
legend_patches.append(mpatches.Patch(color=plot_cols[1], label='UK'))
ax2.set_ylabel('UK Domestic Energy Emissions per Capita (tCO2/capita)')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, title='Country', handles=legend_patches)

ax.tick_params(axis='x', labelrotation=90); ax.set_xlabel('');
plt.axvline(2.5, c='k', linestyle=':'); plt.axvline(5.5, c='k', linestyle=':'); 
plt.savefig(plot_path + 'outputs/plots/barplot_jp_up_co2_twin.png', dpi=200, bbox_inches='tight'); plt.show()


# Spend
means_scaled = cp.copy(means_all).set_index(['Country', 'hhld_comp'])['domestic_energy_spend'].unstack('Country').reset_index()
cols = ['#DE832A', '#3572A0']

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
cols = ['#DE832A', '#3572A0']

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

