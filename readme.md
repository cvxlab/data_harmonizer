# pyESM data harmonization

## Description
This folder contains the required raw data to feed the pyESM model for MIMO along with the code useful to harmonize such data in the final format desired by the model
The code must be used separately for each table: the DataHarmonizer class is initialized for a single table.

## Folder Structure
```
folder/
├── README.md                   # This file
├── main.py                     # Main script to run
├── src                         # Source code
```

## Preliminary steps
- In the src folder, set up the "paths.yml" file by specificying your "main_folder" path (use your initials)
- "pre_harmonization_folder" targets a folder where a subfolder for each table and file required to fill each table is stored. This will be the folder where the harmonization maps files (hmap.xlsx) will be saved and parsed via the "get_data_map_template" and "read_data_map_template" methods respectively
- "empty_model_data_folder" targets the folder containing the empty model input files to be filled. They should be empty so that the filling progress (i.e. how much data are still missing) could be tracked 
- "model_structure" targets the main Excel file containing all info about the model

## Usage
- The code works in the usual pyesm Python environment
- Open the "main.py" script and indicate your initials as "user"
- Once you selected the table you want to fill, open the "src/tables_files_map.yml" file and add the table
- For each table, you need to specify which files you need raw data from, along with their metadata. The mandatory information to specify here are:
    - "sets_to_columns_map" (mapping table coordinates with raw data file columns)
    - "values" (mapping the column of raw data file storing values)
    - "path" (reporting the path to the raw data file, excluding the one reported as "main_dir")
N.B. The raw data files, for the moment, must be in flat csv formats
- Run the main.py script
    - load dependencies and yml files
    - provide the name of a table and initialize the DataHarmonizer class
    - "get_data_map_template" will generate a "hmap_empty.xlsx" file in the "pre_harmonization/<table>/<file>" for each of the raw data files required to fill the given table
    - "read_data_map_template" will load all the "hmnap.xslx" files (the user must rename the file removing the "empty" string manually). It is possible to provide a list with a subset of files, but by default it will parse the harmonization maps of all the files
    - "parse_mapped_raw_data" will parse the each raw data input file according to its path, as provided in the "tables_files_map.yml" file  
    - "harmonize_data" will apply all the modifications to the raw data according to instructions provided in the "hmap.xlsx" files
    - "export" will export an excel file in the model format. By default, the "post_harmonization_folder/<table>.xlsx" path will be adopted, unless another path is provided

    
