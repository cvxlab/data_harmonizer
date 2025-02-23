# pyESM data harmonization

## Description
This folder contains the required raw data to feed the pyESM model for MIMO along with the code useful to harmonize such data in the final format desired by the model
The code must be used separately for each table: the DataHarmonizer class is initialized for a single table.

## Folder Structure
```
folder/
├── README.md                   # This file
├── main.py                     # main script to run
├── src                         # folder with source code
├── harmonization_maps          # folder containing for each table, the templates to indicate how to map raw data files with final model format
```

## Preliminary steps
- In the src folder, set up the "paths.yml" file by specificying your "common_dir" path (use your initials)
- model_structure targets the main Excel file containing all info about the model
- empty_model_data_folder targets the folder containing the empty model input files to be filled 

## Usage
- The code works in the usual pyesm Python environment
- Open the "main.py" script and indicate your initials as "user"
- Once you selected the table you want to fill, open the "src/tables_files_map.yml" file and add the table
- For each table, you need to specify which files you need raw data from, along with their metadata. The mandatory information to specify here are:
    - "sets_to_columns_map" (mapping table coordinates with raw data file columns)
    - "values" (mapping the column of raw data file storing values)
    - "path" (reporting the path to the raw data file, excluding the one reported as "common_dir")
N.B. The raw data files, for the moment, must be in flat csv formats
- Run the main.py script, including the "get_data_map_template" method, in case you also need to generate the template file to be filled. It will be stored in "harmonization_maps/<table_name>/<file_name>"

