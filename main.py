#%%
import pandas as pd
import os
import yaml
from src.data_harmonization import DataHarmonizer

user = 'LR' # specifies the user

# Load the table to file map from the YAML file
with open('src/tables_files_map.yml', 'r') as file:
    tables_files_map = yaml.safe_load(file)

# Load the paths from the YAML file
with open('src/paths.yml', 'r') as file:
    paths = yaml.safe_load(file)
    shared_folder = paths['common_dir'][user]
    model_structure = paths['model_structure']['path']
    empty_model_data_folder = paths['empty_model_data_folder']['path']


#%% Harmonize data
table = 'E_hist_ex' # specifies the table to be harmonized
DH = DataHarmonizer(
    table, 
    tables_files_map[table], 
    shared_folder, 
    model_structure,
    empty_model_data_folder,
)

#%% Export data map templates
# DH.get_data_map_template()

# %% Read back the data map template filled + re-export it adding merge-split info
DH.read_data_map_template()

# %% Parse raw data already filtered accoding to the maps
DH.parse_mapped_raw_data()

# %% Harmonize the data
DH.harmonize_data(report_missing_values=True)

# %% Export harmonized data
DH.export(
    path = "choseyourpath.xlsx"
)

# %%
