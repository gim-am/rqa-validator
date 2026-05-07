from typing import List
from config import settings

from ..common.list_matching import FuzzMatch, match_list_to_list
from ..models.base import   SchemaSheetMap
from ..validators.base import ValidationResult, SeverityLevel
from .base import  DataColumnMap


def match_excel_columns_to_schema( excel_columns: List, schema_sheet: SchemaSheetMap):
        results: List[ValidationResult] = []
        matches: List[DataColumnMap] = []

        for column in schema_sheet.mandatory_columns:
            literal_matches, fuzzy_matched_values = match_list_to_list(column.combine(), 
                                                                       excel_columns,
                                                                       fuzzy_match=settings.FUZZY_MATCH_SHEETS)

            if literal_matches:
                if len(literal_matches) == 1:
                    # because the schema is prevalidated there should only
                    # be one literal match unless there are multiple alternate 
                    # name matches
                    matches.append(DataColumnMap(data_column_name=literal_matches[0]
                                             ,schema_column_name = column.standard_name))
                    
                else:
                    # ideally this should not happen
                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} had {len(literal_matches)} matches to  columns. There should be only 1. Check the schema. Literal matches: {literal_matches}.'
                                    ,severity = SeverityLevel.ERROR
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))   
                continue
            elif fuzzy_matched_values:
                if len(fuzzy_matched_values[0].matches) == 1:
                    matches.append(DataColumnMap(data_column_name=fuzzy_matched_values[0].standard_name
                                             ,schema_column_name = column.standard_name))

                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} was fuzzy matched with an excel column via column name/s and score/s {fuzzy_matched_values[0].matches}.'
                                    ,severity = SeverityLevel.INFO
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))  
                else:
                    results.append(ValidationResult(
                                    rule = 'Match excel column to schema',
                                    message = f'The schema sheet {schema_sheet.standard_name} column {column.standard_name} was fuzzy matched with multiple excel columns so was not matched as this would cause validation errors. Matching results: schema column name/s and score/s {fuzzy_matched_values}.'
                                    ,severity = SeverityLevel.ERROR
                                    ,sheet_name = schema_sheet.standard_name
                                    , column_name=column.standard_name
                                    ))  
        return results, matches

def match_excel_sheet_to_schema( excel_sheet_name: str, schema_sheets: List[SchemaSheetMap]) -> tuple[str, List[ValidationResult]]:
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
                                ,severity = SeverityLevel.INFO
                                ,sheet_name = excel_sheet_name
                                ))     
            return  fuzzy_matched_values_schema[0].standard_name, results
        else:
            # fuzzy match to multiple schema sheets
            results.append(ValidationResult(
                                rule = 'Match excel sheeet to schema',
                                message = f'Excel sheet {excel_sheet_name} was fuzzy matched with multiple schema sheets via schema sheet name/s and score/s  {fuzzy_matched_values_schema} so was not matched. This will lead to validation errors about excel sheets not being found.'
                                ,severity = SeverityLevel.INFO
                                ,sheet_name = excel_sheet_name
                                ))    
            
    return str(), results