from dataclasses import dataclass, field

import fastexcel
import polars as pl
from pathlib import Path
from typing import List

from .base import SheetMap, ColumnMap
from ..validators.base import ValidationResult
from ..models.base import   SheetMapping
from ..models.base_dataset import BaseDatasetSchema
from ..common.list_matching import FuzzMatch, match_list_to_list
from config import settings


@dataclass
class ExcelLoaderData:
    loaded_sheets: List[SheetMap] = field(default_factory=list)
    unloaded_sheets: List[SheetMap] = field(default_factory=list)
    unexpected_sheets: List = field(default_factory=list)

    def get_loaded_sheet_mapped_names(self) -> List[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.schema_sheet_name for sheet in self.loaded_sheets]
    
    def get_unloaded_sheet_mapped_names(self) -> List[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.schema_sheet_name for sheet in self.unloaded_sheets]
    
    def get_loaded_sheet(self, sheet_name: str)  -> SheetMap | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            SheetMap | None: Loaded sheet details if found
        """
        for sheet in self.loaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                return sheet
        return None
    
    def get_sheet_matches(self, sheet_name: str) -> List[SheetMap]:
        """Gets all the sheets matched with a given schema_name.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            List[SheetMap] | None: Loaded sheet details if found
        """
        sheets: List[SheetMap] = []
        for sheet in self.loaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                sheets.append(sheet)

        for sheet in self.unloaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                sheets.append(sheet)

        return sheets

class ExcelLoader:

    def __init__(self, schema_config: BaseDatasetSchema):
        self.schema = schema_config

    def load(self, filepath: Path)   -> tuple[ExcelLoaderData, List[ValidationResult]]:
        """Loads an excel file, does some checking and sorting of the sheets.

        Args:
            filepath (Path): Filepath of excel file. Might change for api call.

        Returns:
            tuple[ExcelLoaderData,  List[ValidationResult]]: 
            class that contains the loaded data, sheets etc,
            list of validation warnings

        """        
        results: List[ValidationResult] = []
        # get a list of excel sheet names
        all_sheets = fastexcel.read_excel(filepath).sheet_names
        # lower sheet names for easier comparison later
        # all_sheets = list(map(str.lower, all_sheets))
        
        data = ExcelLoaderData()
        
        for excel_sheet_name in all_sheets:

            l_mapped_name, l_results = self.match_excel_sheet_to_schema(excel_sheet_name, self.schema.schema_loaded_sheets)
            u_mapped_name, u_results = self.match_excel_sheet_to_schema(excel_sheet_name, self.schema.schema_unloaded_sheets)
            
            # pre schema validation will throw error if any sheets have matching names or alternate names
            # as well as if any columns within a sheet are duplicated (via names or alternate names)
            # so there should not be both l_mapped_name and u_mapped_name for literal matches
            # options
            # 1: l_mapped_name, not l_results > literal match on loaded sheets
            # 2: u_mapped_name, not u_results > literal match on unloaded sheets
            # 3: l_mapped_name, l_results, not u_mapped_name > fuzzy match on loaded sheets
            # 4: u_mapped_name, u_results > fuzzy match on unloaded sheets
            # 5: l_mapped_name and u_mapped_name > error fuzzy matching
            # 6: not l_mapped_name, not u_mapped_name, (u_results or l_results) > error fuzzy matching
            # 7: unexpected sheet > no matching

            # 5
            if (l_mapped_name and l_results and u_mapped_name and u_results):
                results.append(ValidationResult(
                                rule = 'Match excel sheeet to schema',
                                message = f'Excel sheet {excel_sheet_name} was fuzzy matched with multiple schema sheets. This will lead to validation errors about excel sheets not being found.'
                                ,severity = 'info'
                                ,sheet_name = excel_sheet_name
                                )) 
            # 6
            elif (not l_mapped_name and not u_mapped_name and (l_results or u_results)):
                results.extend(l_results)
                results.extend(u_results)

            # 1 and 3
            elif (l_mapped_name and (not l_results or 
                                   (l_results and ( not( u_mapped_name and not u_results)
                                                   or not u_mapped_name)))):
                # sheets that are expected and loaded for further data validation
                df: pl.DataFrame = pl.read_excel(source=filepath, sheet_name=excel_sheet_name)
                df = df.rename(str.lower)
                df_columns = df.columns

                schema_sheet = self.schema.get_schema_loaded_sheet(l_mapped_name)
                if schema_sheet is not None:
                    # it should not be none as it was just matched.
                    column_results, column_matches = self.match_excel_columns_to_schema(df_columns, schema_sheet)
                    data.loaded_sheets.append(SheetMap(schema_sheet_name=l_mapped_name,
                                                      data_sheet_name = excel_sheet_name,
                                                      data=df,
                                                      data_columns=df_columns,
                                                      column_map=column_matches))    
                    results.extend(l_results) 
                    results.extend(column_results)  
                else:
                    results.append(ValidationResult(
                                    rule = 'Getting Schema Sheet',
                                    message = f'The schema sheet {l_mapped_name} was not found.'
                                    ,severity = 'error'
                                    ,sheet_name = l_mapped_name
                                    )) 
                    continue                
                
                          
            # 2, 4
            elif (u_mapped_name ):
                # sheets that are expected but dont need to be loaded
                data.unloaded_sheets.append(SheetMap(schema_sheet_name=u_mapped_name,
                                                     data_sheet_name=excel_sheet_name))
                results.extend(u_results)
            else:
                # 7
                data.unexpected_sheets.append(excel_sheet_name)

        return data, results
    

    
    def match_excel_columns_to_schema(self, excel_columns: List, schema_sheet: SheetMapping):
        results: List[ValidationResult] = []
        matches: List[ColumnMap] = []

        for column in schema_sheet.mandatory_columns:
            literal_matches, fuzzy_matched_values = match_list_to_list(column.combine(), 
                                                                       excel_columns,
                                                                       fuzzy_match=settings.FUZZY_MATCH_SHEETS)

            if literal_matches:
                if len(literal_matches) == 1:
                    # because the schema is prevalidated there should only
                    # be one literal match unless there are multiple alternate 
                    # name matches
                    matches.append(ColumnMap(data_column_name=literal_matches[0]
                                             ,schema_column_name = column.standard_name))
                    
                else:
                    # ideally this should not happen
                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} had {len(literal_matches)} matches to  columns. There should be only 1. Check the schema. Literal matches: {literal_matches}.'
                                    ,severity = 'error'
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))   
                continue
            elif fuzzy_matched_values:
                if len(fuzzy_matched_values[0].matches) == 1:
                    matches.append(ColumnMap(data_column_name=fuzzy_matched_values[0].standard_name
                                             ,schema_column_name = column.standard_name))

                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} was fuzzy matched with an excel column via column name/s and score/s {fuzzy_matched_values[0].matches}.'
                                    ,severity = 'info'
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))  
                else:
                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} was fuzzy matched with multiple excel columns so was not matched as this would cause validation errors. Matching results: schema column name/s and score/s {fuzzy_matched_values}.'
                                    ,severity = 'error'
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))  
        return results, matches

    def match_excel_sheet_to_schema(self, excel_sheet_name: str, schema_sheets: List[SheetMapping]) -> tuple[str, List[ValidationResult]]:
        """Trys to match an excel sheet name to a schema sheet name. 
            
            First, a literal match is attempted. If one is found this 
            is returned

            If there is no literal match and fuzzy matching is enabled
            then a fuzzy match is attempted. If a match is made to only
            one sheet then this is returned. If a match is made to more than 
            one sheet then no match is returned.
        Args:
            sheet_name (str): excel sheet to be matched
            schema_sheets (List[SheetMapping]): schema sheets to match to. 

        Returns:
            tuple[str, List[ValidationResult]]: the schema sheet standard name
            if matched, a list of any validation warnings if relevant.
        """
        results: List[ValidationResult] = []
        fuzzy_matched_values_schema: List[FuzzMatch] = []

        for sheet_config in schema_sheets:

            literal_matches, fuzzy_matched_values = match_list_to_list(sheet_config.combine_sheet_names(), 
                                                                       [excel_sheet_name],
                                                                       fuzzy_match=settings.FUZZY_MATCH_SHEETS)

            if literal_matches:
                # clear warning as they are not relevant if a literal match is found
                results = []
                return sheet_config.standard_name, results
            elif fuzzy_matched_values:
                fuzzy_matched_values_schema.extend(fuzzy_matched_values)

        if fuzzy_matched_values_schema:
            if len(fuzzy_matched_values_schema) == 1:
                # fuzzy match to only 1 schema sheet
                results.append(ValidationResult(
                                    rule = 'Match excel sheeet to schema',
                                    message = f'Excel sheet {excel_sheet_name} was fuzzy matched with schema sheet {fuzzy_matched_values_schema[0].standard_name} via schema sheet name/s and score/s {fuzzy_matched_values_schema[0].matches}.'
                                    ,severity = 'info'
                                    ,sheet_name = excel_sheet_name
                                    ))     
                return  fuzzy_matched_values_schema[0].standard_name, results
            else:
                # fuzzy match to multiple schema sheets
                results.append(ValidationResult(
                                    rule = 'Match excel sheeet to schema',
                                    message = f'Excel sheet {excel_sheet_name} was fuzzy matched with multiple schema sheets via schema sheet name/s and score/s  {fuzzy_matched_values_schema} so was not matched. This will lead to validation errors about excel sheets not being found.'
                                    ,severity = 'info'
                                    ,sheet_name = excel_sheet_name
                                    ))    
                
        return str(), results
