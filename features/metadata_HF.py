import argparse
import os
import sys
import pandas as pd
import numpy as np
# import re

'''
TODO:   - Devise date/time processing method
        - Remove "Pneumonia Output" section
        - Remove wheezing etc. sections
'''

def process_metadata(patient_data_path, output_path):
    """Data wrangler that turns research coordinator input into usable form"""
    if not patient_data_path:
        print('missing patient data file paths')
        sys.exit(-1)

    patient_data = pd.read_csv(patient_data_path).as_matrix()
    DEFAULT_SMOKING_PACKS = 0
    DEFAULT_TEMP = 98.6
    DEFAULT_BP_SYSTOLIC = 130
    DEFAULT_BP_DIASTOLIC = 85
    DEFAULT_HR = 90
    DEFAULT_RR = 18
    DEFAULT_HEIGHT = 170
    DEFAULT_BNP = 0
    KNOWN_BAD_IDS = []

    def default_thorax_circ(gender):
        if gender == 'M':
            return 80
        else:
            return 80

    def to_float(s):
        try:
            return float(s)
        except ValueError:
            return False

    def process_row(index):
        """Main processing function for parent call"""
        row_data = patient_data[index, :]
        processed_row = np.array([])

        id = row_data[0]
        # return [] if bad data, empty rows are ignored by parent
        if id in KNOWN_BAD_IDS:
            return processed_row

        processed_row = np.append(processed_row, id)

        # Process length of stay

        # DOES NOT WORK
        # admis_df = pd.DataFrame(np.array(row_data[1]))
        # admis_df = pd.to_datetime(admis_df, format='%d/%b/%Y')
        # disch_df = pd.DataFrame(np.array(row_data[2]))
        # disch_df = pd.to_datetime(disch_df, format='%d/%b/%Y')
        # term = (disch_df - admis_df).days
        # processed_row = np.append(processed_row, term)
        processed_row = np.append(processed_row, 1)

        #process age
        procesed_row = np.append(processed_row, row_data[3])

        #process gender
        gender = row_data[4]
        if gender != 'M' and gender != 'F':
            print 'Row %d: Bad gender: %s' % (index, gender)
            return np.array([])
        processed_row = np.append(processed_row, 1 if gender == 'M' else 0)
        processed_row = np.append(processed_row, 1 if gender == 'F' else 0)

        # process height
        height = to_float(row_data[6])
        if not isinstance(height, float):
            height = DEFAULT_HEIGHT
        processed_row = np.append(processed_row, height)

        # process weight
        weight = row_data[7]
        processed_row = np.append(processed_row, weight)

        #process thorax circumference
        thorax_circ = to_float(row_data[8])
        if not isinstance(thorax_circ, float):
            print "USING DEFAULT thorax_circ"
            print thorax_circ
            print type(thorax_circ)
            thorax_circ = default_thorax_circ(gender)
        processed_row = np.append(processed_row, thorax_circ)

        # process smoking history
        smoking_packs = to_float(row_data[9])
        if not isinstance(smoking_packs, float):
            smoking_packs = DEFAULT_SMOKING_PACKS
        processed_row = np.append(processed_row, smoking_packs)

        # process comorbities
        comorbities = 0
        if row_data[10] != 'n/a':
            comorbities = 1
        processed_row = np.append(processed_row, comorbities)

        #process BNP (metric which correlated with HF)
        bnp = to_float(processed_row[11])
        if not isinstance(bnp, float):
            bnp = DEFAULT_BNP
        processed_row = np.append(processed_row, bnp)

        # process temperature
        temp = to_float(row_data[12])
        if not isinstance(temp, float):
            temp = DEFAULT_TEMP
        processed_row = np.append(processed_row, temp)

        #process blood pressure
        bp = row_data[13] # 120/80
        parts = bp.split('/')
        if len(parts) == 2:
            bp_systolic = to_float(parts[0])
            bp_diastolic = to_float(parts[1])
            if not isinstance(bp_systolic, float) and isinstance(bp_diastolic, float):
                bp_systolic = DEFAULT_BP_SYSTOLIC
                bp_diastolic = DEFAULT_BP_DIASTOLIC
        else:
            bp_systolic = DEFAULT_BP_SYSTOLIC
            bp_diastolic = DEFAULT_BP_DIASTOLIC
        processed_row = np.append(processed_row, bp_systolic)
        processed_row = np.append(processed_row, bp_diastolic)

        # process heart rate
        hr = to_float(row_data[14])
        if not isinstance(hr, float):
            hr = DEFAULT_HR
        processed_row = np.append(processed_row, hr)

        # process respiratory rate
        rr = to_float(row_data[15])
        if not isinstance(rr, float):
            rr = DEFAULT_RR
        processed_row = np.append(processed_row, rr)

        # process oxygen saturation
        spo02 = to_float(row_data[16])
        processed_row = np.append(processed_row, spo02)

        # process peak flow 1
        peak_flow = to_float(row_data[17])
        processed_row = np.append(processed_row, peak_flow)

        #second peak flow dataset is incomplete, excluding for now

        return processed_row

    [rows, cols] = patient_data.shape

    # Headers are unique to each metadata csv,
    # size must agree with patient_data cols
    headers = ['id', 'stay_length', 'age', 'male', 'female', 'height',
     'weight', 'thorax_circ', 'smoking_packs', 'comorbities', 'bnp', 'temp',
      'bp_systolic', 'bp_diastolic', 'hr', 'rr', 'sp02','peak_flow_1']

    output_data = np.array([])
    for row_index in range(3, rows):
        next_row = process_row(row_index)
        if next_row.size != 0:
            if output_data.size == 0:
                output_data = next_row
            else:
                output_data = np.vstack([output_data, next_row])
    df = pd.DataFrame(data=output_data, columns=headers)
    df.to_csv(output_path, index=False, line_terminator='\n')