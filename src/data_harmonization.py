#%%
import pandas as pd
import os

#%% Class to harmonize data
class DataHarmonizer:
    def __init__(
            self, 
            table:str,
            table_file_map:dict,
            main_folder:str,
            pre_harmonization_folder: str,
            post_harmonization_folder: str,
            empty_model_data_folder:str,
            model_structure_path:str,
        ):

        self.table = table
        self.raw_data = {}
        self.main_dir = main_folder
        self.pre_harmonization_dir = pre_harmonization_folder
        self.post_harmonization_dir = post_harmonization_folder
        self.empty_model_data_folder = empty_model_data_folder

        self.table_file_map = table_file_map

        print(f"Reading model structure from {model_structure_path}")
        self.model_structure = pd.read_excel(
            os.path.join(self.main_dir, model_structure_path),
            sheet_name=None,
        )

        print(f"Reading model mask from {self.empty_model_data_folder}")
        self.model_mask = pd.read_excel(
            os.path.join(self.main_dir, self.empty_model_data_folder, f"{self.table}.xlsx"), 
            sheet_name=self.table
        ) 

    def get_data_map_template(
            self,
            model: str = 'phy',
            capacity_unit: bool = False,
        ):
            
            for file,info in self.table_file_map.items():
                print(f"Creating data map template for {file}")

                # Create a new Excel writer object
                sets_to_columns_map = info['sets_to_columns_map']

                table_dir = os.path.join(self.main_dir, self.pre_harmonization_dir, self.table, file)
                if not os.path.exists(table_dir):
                    os.makedirs(table_dir)
                
                with pd.ExcelWriter(f"{table_dir}/hmap_empty.xlsx", engine='openpyxl') as writer:

                    # For each column in the dataframe, create a new sheet with unique values
                    for column in self.model_mask.columns:
                        if column not in ['id', 'values']:
                            unique_values = self.model_mask[column].dropna().unique()
                            set_name = column.split("_")[0]
                            units = self.get_set_units(set_name=set_name,model=model,capacity=capacity_unit)
                            df_unique = pd.DataFrame({set_name: unique_values})

                            df_unique['merge_split'] = ''
                            df_unique['merge_split_values'] = ''
                            df_unique['notes'] = ''    
                            df_unique[sets_to_columns_map[set_name]] = ""

                            if not units.empty:
                                df_unique['units'] = ""
                                df_unique['raw_units'] = ''
                                df_unique['unit_conversion'] = ''
                                df_unique['units'] = df_unique[set_name].map(units.iloc[:,0])
                                df_unique.set_index([set_name, 'units', 'raw_units','unit_conversion'], inplace=True)
                                df_unique.reset_index(inplace=True)

                            df_unique.to_excel(writer, sheet_name=set_name, index=False)

                    # Add an empty "files" sheet
                    info_for_export = info.copy()
                    info_for_export.pop('sets_to_columns_map', None)
                                        
                    files_df = pd.DataFrame.from_dict(info_for_export, orient='index').reset_index()
                    files_df.columns = ['label', 'value']
                    files_df.to_excel(writer, sheet_name='metadata', index=False)


    def get_set_units(
            self,
            set_name: str,
            model: str,
            capacity: bool,
    ):
        set_df_name = "_set_"+set_name.upper()
        set_df = self.model_structure[set_df_name]

        if capacity:
            column  = set_name+'_'+model+'capacity_unit'
        else:
            column  = set_name+'_'+model+'_unit'

        if column not in set_df.columns:
            units_df = pd.DataFrame()
            return units_df
        
        units_df = set_df.loc[:,[set_name+'_Name',column]]
        units_df.set_index(set_name+'_Name', inplace=True)
        units_df.dropna(inplace=True)
        
        return units_df


    def read_data_map_template(
            self,
            files:list = 'all',
    ):
        
        if files == 'all':
            files = os.listdir(os.path.join(self.main_dir, self.pre_harmonization_dir, self.table))
            files = [f for f in files if f != ".DS_Store"] # remove hidden files
        
        maps = {}
        for file in files:
            print(f"Reading data map for {file}")
            maps[file] = pd.read_excel(os.path.join(self.main_dir, self.pre_harmonization_dir, self.table, file, 'hmap.xlsx'), sheet_name=None)
            for sheet_name, df in maps[file].items():
                if sheet_name in self.table_file_map[file]['sets_to_columns_map']:
                    maps[file][sheet_name] = df.dropna(axis=0, how='all', subset=df.columns[1:])
                    maps[file][sheet_name].set_index([i for i in maps[file][sheet_name].columns if i != self.table_file_map[file]['sets_to_columns_map'][sheet_name]], inplace=True)
                    maps[file][sheet_name] = maps[file][sheet_name].apply(lambda x: x.astype(str).str.split('+').explode()).reset_index()

        self.data_map = maps
    

    def parse_mapped_raw_data(
            self,
            files: list = 'all',
            filter_mapped: bool = True,
    ):
        
        if self.raw_data != {}:
            overwrite = input("Raw data already exists. Do you want to overwrite it? (y/n): ")
            if overwrite.lower() == 'y':
                self.raw_data = {}
            else:
                return

        if not hasattr(self, 'data_map'):
            print("Data map not found. Reading it with default parameters.")
            self.read_data_map_template(files=files)

        if files == 'all':
            files = list(self.data_map.keys())

        for file in files:
            print(f"Parsing raw data for {file}")
            info = self.data_map[file].copy()
            info['metadata'].set_index('label', inplace=True)
            file_path = os.path.join(self.main_dir, info['metadata'].loc['path','value'])

            self.raw_data[file] = pd.read_csv(file_path)
            
            columns_to_keep = []
            for set_name, df in info.items():
                if set_name != 'metadata':
                    if set_name in self.table_file_map[file]['sets_to_columns_map']:

                        column_name = self.table_file_map[file]['sets_to_columns_map'][set_name]
                        mapped_labels = self.data_map[file][set_name][column_name]
                        mapped_labels = mapped_labels.dropna()
                        mapped_labels = mapped_labels[mapped_labels != 'nan']

                        if set_name == 'years':
                            mapped_labels = mapped_labels.astype('float').astype('int64')

                        self.raw_data[file] = self.raw_data[file].query(f"{column_name} in @mapped_labels")
                        columns_to_keep.append(column_name)

            value_column = self.table_file_map[file]['values']
            columns_to_keep.append(value_column)

            self.raw_data[file] = self.raw_data[file].loc[:,columns_to_keep].fillna(0)
            info['metadata'].reset_index(inplace=True)            


    def harmonize_data(
            self,
            files: list = 'all',
            report_missing_values = False,
    ):

        if self.raw_data == {}:
            print("No raw data to harmonize. Please parse the raw data first.")
            return

        harmonized_data = self.model_mask.copy()

        if files == 'all':
            files = list(self.raw_data.keys())

        for file in files:
            print(f"Harmonizing data for {file}")

            # Extract mapping for this file
            # column_mapping = {v:k+"_Name" for k,v in self.table_file_map[file]['sets_to_columns_map'].items()}
            column_mapping = {v:k+"_Name" for k,v in self.table_file_map[file]['sets_to_columns_map'].items()}
            
            value_column_origin = self.table_file_map[file]['values']  # The name of the values column in raw_data
            
            # Rename columns in raw_data to match harmonized_data
            raw_data_renamed = self.raw_data[file].copy()
            raw_data_renamed = raw_data_renamed.rename(columns=column_mapping)
            raw_data_renamed = raw_data_renamed.rename(columns={value_column_origin: 'values'}).fillna(0)
            
            
            for set_name,column_name in self.table_file_map[file]['sets_to_columns_map'].items():
                if set_name != 'metadata':

                    map_df = self.data_map[file][set_name].copy()
                    # map_df = map_df.drop([c for c in map_df.columns if c not in [column_name,set_name]],axis=1)
                    map_df = map_df[map_df[column_name] != 'nan']
                    map_df.set_index(set_name,inplace=True)
                    map_df = map_df.rename(columns={column_name: set_name+"_Name"})
                    map_df.reset_index(inplace=True)

                    # map_df.set_index(column_name,inplace=True)

                    # raw_data_renamed[set_name+"_Name"] = raw_data_renamed[set_name+"_Name"].map(map_df[set_name])
                    if set_name == 'years':
                        map_df['years_Name'] = map_df['years'].astype('float').astype('int64')
                    raw_data_renamed = raw_data_renamed.merge(map_df, on=set_name+"_Name", how='left')

                    # converting unit of measure of the values column according to unit_conversion column
                    if 'unit_conversion' in raw_data_renamed.columns:
                        raw_data_renamed['values'] = raw_data_renamed.apply(
                            lambda row: row['values'] * row['unit_conversion'] if pd.notna(row['unit_conversion']) else row['values'], 
                            axis=1
                        )

                    # multiplying values by the shares in case merge_split column contains share
                    if 'merge_split' in raw_data_renamed.columns:
                        raw_data_renamed['values'] = raw_data_renamed.apply(
                            lambda row: row['values'] * row['merge_split_values'] if pd.notna(row['merge_split_values']) else row['values'], 
                            axis=1
                        )

                    # renaming columns
                    raw_data_renamed.drop(columns=[set_name+"_Name"], inplace=True)
                    raw_data_renamed.rename(columns={set_name: set_name+"_Name"}, inplace=True)

                    # dropping unnecessary columns
                    columns_to_drop = [c for c in raw_data_renamed.columns if c not in column_mapping.values() and c != 'values' and c != 'merge_split']
                    raw_data_renamed.drop(columns=columns_to_drop, inplace=True)

                    # summing values with groupby in case merge_split column contains sum
                    if 'merge_split' in raw_data_renamed.columns:
                        raw_data_renamed_to_sum = raw_data_renamed.query(f"merge_split == 'sum'")
                        if not raw_data_renamed_to_sum.empty:
                            raw_data_renamed_to_sum.set_index([c for c in raw_data_renamed_to_sum.columns if c != 'values'], inplace=True)
                            raw_data_renamed_to_sum = raw_data_renamed_to_sum.groupby(level=[c for c in raw_data_renamed_to_sum.index.names if c != 'merge_split']).sum()
                            raw_data_renamed_to_sum.reset_index(inplace=True)

                        # dropping rows with merge_split column containing sum
                        raw_data_renamed = raw_data_renamed.query(f"merge_split != 'sum'")
                        raw_data_renamed.drop(columns=['merge_split'], inplace=True)
                        
                    # appending the sum of values to the dataframe
                    if not raw_data_renamed_to_sum.empty:
                        raw_data_renamed = pd.concat([raw_data_renamed, raw_data_renamed_to_sum], axis=0) 
                        
                    raw_data_renamed.index = range(len(raw_data_renamed))  # resetting index

            raw_data_renamed.drop_duplicates(inplace=True)
            raw_data_renamed.set_index([c for c in raw_data_renamed.columns if c != 'values'], inplace=True)
            harmonized_data.set_index([c for c in harmonized_data.columns if c not in ['id','values']], inplace=True)

            harmonized_data.update(raw_data_renamed)

            raw_data_renamed.reset_index(inplace=True)
            harmonized_data.reset_index(inplace=True)

            # Ensure 'id' column is the first one
            cols = harmonized_data.columns.tolist()
            if 'id' in cols:
                cols.insert(0, cols.pop(cols.index('id')))
                harmonized_data = harmonized_data[cols]

        self.harmonized_data = harmonized_data


        if report_missing_values:
            missing_values = self.harmonized_data[self.harmonized_data.isna().any(axis=1)]
            print("Overall missing values %: ", missing_values.shape[0]/self.harmonized_data.shape[0]*100, "%")
            
            if missing_values.shape[0] > 0:
                for column in missing_values.columns:
                    if column != 'values':
                        unique_values = missing_values[column].dropna().unique()
                        print(f"\nUnique values in column '{column}': {unique_values}")

    def export(
            self,
            path: str = None,
    ):
        if path == None:
            path = os.path.join(self.main_dir, self.post_harmonization_dir, f"{self.table}.xlsx")

        print(f"Exporting harmonized data to {path}")
        self.harmonized_data.to_excel(path, index=False, sheet_name=self.table)
# %%
