# todo: move these to "data_dir" these constants shouldn't be included in any package
import numpy as np
mimic_thresholds = {
    'Diastolic blood pressure': [80, 90, 120],
    'Fraction inspired oxygen': [0.5],
    'Glascow coma scale total':[9, 13],
    'Glucose': [140, 200], 
    'Heart Rate': [60, 100, 140],
    'Mean blood pressure': [70, 100, 115, 150],
    'Oxygen saturation': [90, 95],
    'Respiratory rate': [12, 16, 20],
    'Systolic blood pressure': [120, 140, 180],
    'Temperature': [36.0, 37.0, 38.0], # deg C
    'Weight': [63, 83, 100], # kg
    'pH': [7.35, 7.45],
    'Age': [34, 49, 65, 79],
    'Gender': ['M', 'F']
}

def build_threshold_dict(col_names, mimic_thresholds):
    thresholds = {}
    for i in col_names:
        if i in mimic_thresholds:
            thresholds[i] = mimic_thresholds[i]
        elif i.endswith('count'):
            thresholds[i] = [1]
        elif i[2:-5] in mimic_thresholds:
            thresholds[i] = mimic_thresholds[i[2:-5]]
        elif i[:-5] in mimic_thresholds:
            thresholds[i] = mimic_thresholds[i[:-5]]
        else:
            print(i)
    return thresholds    

seq_grids = {
    'heart': {
        'N': list(range(1, 14)),
        'M': list(range(1, 6)),
        'FNR': np.arange(0.1, 1.01, 0.1)        
    }   
}
seq_grids['mort'] = seq_grids['heart']