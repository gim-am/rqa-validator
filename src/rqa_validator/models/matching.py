from dataclasses import dataclass, field
from typing import Dict, List
from thefuzz import fuzz
from thefuzz import process
from ..models.schema import SheetMapping
from ..validators.base import ValidationResult
from config import settings

@dataclass
class FuzzMatch():
    standard_sheet_name: str
    matches: Dict = field(default_factory=dict) 

def match_excel_sheet_to_schema( sheet_name: str, schema_sheets: List[SheetMapping]) -> tuple[str, List[ValidationResult]]:
    results: List[ValidationResult] = []

    fuzzy_matched_values: List[FuzzMatch] = []
    for sheet_config in schema_sheets:
        if sheet_config.matches(sheet_name):
            # clear warning as they are not relevant if a literal match is found
            results = []
            return sheet_config.standard_name, results
        elif settings.FUZZY_MATCH_SHEETS:
            fuz_match =  process.extract(sheet_name, sheet_config.combine_sheet_names(), limit=2, scorer=fuzz.WRatio)
            fuz_filter= [match for match in fuz_match if match[1] > 90]
            if fuz_filter:
                fuzzy_matched_values.append(FuzzMatch(sheet_config.standard_name,
                                                       dict(fuz_filter)))

    if fuzzy_matched_values:
        if len(fuzzy_matched_values) == 1:
            results.append(ValidationResult(
                                rule = 'Match excel sheeet to schema',
                                message = f'Excel sheet {sheet_name} was fuzzy matched with schema sheet {fuzzy_matched_values[0].standard_sheet_name} via schema sheet name/s and score/s {fuzzy_matched_values[0].matches}.'
                                ,severity = 'info'
                                ,sheet_name = sheet_name
                                ))     
            return  fuzzy_matched_values[0].standard_sheet_name, results
        else:
            results.append(ValidationResult(
                                rule = 'Match excel sheeet to schema',
                                message = f'Excel sheet {sheet_name} was fuzzy matched with multiple schema sheets via schema sheet name/s and score/s  {fuzzy_matched_values} so was not matched. This will lead to validation errors about excel sheets not being found.'
                                ,severity = 'info'
                                ,sheet_name = sheet_name
                                ))    
            
    return str(), results
