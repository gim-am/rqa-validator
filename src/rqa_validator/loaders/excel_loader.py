from dataclasses import dataclass, field

import fastexcel
import polars as pl
from pathlib import Path
from typing import List
from thefuzz import fuzz
from thefuzz import process

from ..validators.base import ValidationResult
from ..models.base import  BaseDatasetSchema, SheetMapping
from ..common.matching import FuzzMatch, match_list_to_list
from config import settings

@dataclass
class LoadedSheet:
    schema_sheet_name:str
    data_sheet_name: str
    data: pl.DataFrame
    # this operation is ran numerous times so might as well store it once here
    columns: List[str]

@dataclass
class ExcelLoaderData:
    loaded_sheets: List[LoadedSheet] = field(default_factory=list)
    unloaded_sheets = []
    unexpected_sheets = []

    def get_loaded_sheet_mapped_names(self) -> List[str]:
        """Gets all the standard names for the loaded excel sheets

        Returns:
            List[str]: List of sheet names.
        """
        return [sheet.schema_sheet_name for sheet in self.loaded_sheets]
    
    def get_loaded_sheet(self, sheet_name: str)  -> LoadedSheet | None:
        """Gets the details and data for a loaded sheet if it exists.

        Args:
            sheet_name (str): Excel sheets to be searched for

        Returns:
            LoadedSheet | None: Loaded sheet details if found
        """
        for sheet in self.loaded_sheets:
            if sheet.schema_sheet_name == sheet_name:
                return sheet
        return None
    

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
        all_sheets = list(map(str.lower, all_sheets))
        
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
                                
                data.loaded_sheets.append(LoadedSheet(schema_sheet_name=l_mapped_name,
                                                      data_sheet_name=excel_sheet_name,
                                                      data=df,
                                                      columns=df.columns))    
                results.extend(l_results)            
            # 2, 4
            elif (u_mapped_name ):
                # sheets that are expected but dont need to be loaded
                data.unloaded_sheets.append(u_mapped_name)
                results.extend(u_results)
            else:
                # 7
                data.unexpected_sheets.append(excel_sheet_name)

        return data, results
    

    
    
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
