#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 11:43:06 2018

@author: yashasaxena
"""
## Script to plot MFCC results over time for a particular patient ##
import pandas as pd
import matplotlib.pyplot as plt
import csv
import scipy
from scipy import stats
import numpy as np
from datetime import datetime, date
#functions
def normalize(df):
    """Normalize a pandas dataframe using min-max normalization, returns a copy"""
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result
#import dataset
filepath = 'HF_results/intertrial_means.csv'
df = pd.read_csv(filepath)
df_indexed = df.set_index(['patient_id','date','localization'])
patient_array = ['HF001', 'HF009', 'HF018']
MFCC = 'mfcc_00'
#create 3 datasets, one each for patient 1,9, 18
patient_datasets = []
for patient in patient_array:
    df_patient = df_indexed.loc[patient,:]
    df_patient = normalize(df_patient)
    df_patient = df_patient.groupby('date').mean()
    first_visit = str(min(df_patient.index))
    first_visit_y = int(first_visit[-2:])
    first_visit_m = int(first_visit[:-4])
    first_visit_d = int((first_visit[:-2])[-2:])
    first_visit = date(first_visit_y, first_visit_m, first_visit_d)
    #create admit days column for time variable
    admit_days = []
    for x in range(len(df_patient.index)):
        index_val = str(df_patient.index[x])
        date_y = int(index_val[-2:])
        date_m = int(index_val[:-4])
        date_d = int((index_val[:-2])[-2:])
        date_visit = date(date_y, date_m, date_d)
        date_diff = date_visit - first_visit
        n_days = date_diff.days
        admit_days.append(n_days)    
    df_patient['admit_days']=admit_days
    #create percentage change column 
    mfcc_pctdelta = []
    for y in range(len(df_patient[MFCC])):
        if y==0:
            prev_val = df_patient[MFCC].values[y]
        else:
            prev_val = df_patient[MFCC].values[y-1]
        val = df_patient[MFCC].values[y]
        pct_delta = (val-prev_val)/val 
        mfcc_pctdelta.append(pct_delta)
    df_patient['mfcc_pctdelta'] = mfcc_pctdelta 
    patient_datasets.append(df_patient)
#plot data
fig, axarr = plt.subplots(3,1, sharex=True, sharey=True)
for n in range(len(patient_datasets)):
    axarr[n].bar( 'admit_days', 'mfcc_pctdelta', data=patient_datasets[n], color='olive')
    