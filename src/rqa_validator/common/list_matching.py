from dataclasses import dataclass, field
from typing import Any, Dict, List
from thefuzz import fuzz
from thefuzz import process

from config import settings
from ..loaders.base import ColumnMap

@dataclass
class FuzzMatch():
    standard_name: str
    matches: Dict= field(default_factory=dict) 




def match_list_to_list(source: List[str],
                        target: List[str],
                        fuzzy_match: bool,
                          fuzzy_match_limit: int = 2,
                          lower_values: bool = True) -> tuple[list[str], List[FuzzMatch]]:
    """Checks if items in a source list are found in a target list. 
        Optionally performs fuzzy matching on columns in the source
        list if there was no literal match found with items in the target
        list.

    Args:
        source (List[str]): list of items to search for
        targets (List[str]): list of items to search against
        fuzzy_match (bool): if fuzzy matching should be performed
        fuzzy_match_limit (int, optional): Max number of fuzzy matches to return. Defaults to 2.

    Returns:
        tuple[list[str], List[FuzzMatch]: a list of literal matches, a list of fuzzy matches.
    """

    

    if lower_values:
        l_source = list(map(str.lower, source))
        l_target = list(map(str.lower, target))
    else:
        l_source = source
        l_target = target

    literal_matches = match_list(l_source, l_target)
    fuzzy_matched_values: List[FuzzMatch] = []

    if fuzzy_match:
        # only do fuzzy match for a column if there was no literal match
        for search_item in filter_list(l_source, literal_matches):
            # check if the items have a similar length
            l_target_tolerance = filter_list_with_tolerance(search_item, l_target)
            
            if l_target_tolerance:
                match_result = process.extractBests(query=search_item, 
                                                choices=l_target_tolerance, 
                                                scorer= fuzz.WRatio,#settings.FUZZY_MATCH_SCORER,
                                                score_cutoff = settings.MIN_FUZZY_MATCH_SCORE,
                                                limit = fuzzy_match_limit)
                
                if match_result:
                    details = FuzzMatch(standard_name=search_item)
                    for match_item in match_result:
                        details.matches[match_item[0]] = match_item[1]
                    
                    fuzzy_matched_values.append(details)
    return literal_matches, fuzzy_matched_values
            
def match_list(source: List, target: List) -> list:
    """Returns items in source that are in target"""
    set_target = set(target)
    return [item for item in source if item in set_target]

def unique_list(source: List) -> list[Any]:
    """returns a list of unique items"""
    return list(set(source))

def filter_list(source: List, target: List) -> list:
    """Returns items in source that are not in target"""
    set_target = set(target) 
    return [item for item in source if item not in set_target]

def filter_list_with_tolerance(source: str, 
                               target: List[str], 
                               tolerance_ratio:float = settings.FUZZY_MATCH_STRING_LENGTH_RATIO) -> List[str]:
    """ Filters a list based on a comparison between the string length
    of source and items in a target list using a tolerance factor.
    
    So strings of a similar enough length will be returned but if the length
    difference is too great then they will not be returned."""
    def _check_length_tolerance(search_item: str, 
                                target_item: str):
        length_search_item = len(search_item)
        length_target_item = len(target_item)
        
        ratio = min(length_target_item, length_search_item) / max(length_target_item, length_search_item)
    
        return ratio >= tolerance_ratio
    
    return [item for item in target if _check_length_tolerance(source, item)]

def duplicate_list_items(source: List) -> list[Any]:
    """returns a list of items that appear in a list multiple times.

    Args:
        source (List): list of items to check

    Returns:
        list[Any]: list of duplicated items. should be unique list.
    """
    return [item for item in set(source) if source.count(item) > 1]


def combine_lists(source: List | None, target: List | None, unique_list: bool = True):
    """Combines two lists returning a unique list"""
    combined_list: List = []    

    if source is not None:
        combined_list.extend(source)
    
    if target is not None:
        combined_list.extend(target)

    if unique_list:
        return list(set(combined_list))
    else:
        return combined_list

def add_to_list(item: str | None, target: List | None) -> list:
    """Adds item and list. returns a unique list."""
    combined_list: List = []    

    if item is not None:
        combined_list.append(item)

    if target is not None:
        combined_list.extend(target)

    return list(set(combined_list))

def is_in_list(item:str, target: List) -> bool:
    """Checks if an item is in a list"""
    return item in target  




def match_sheet_columns(source:List[ColumnMap], target:List[ColumnMap] ):
    """matches columns between two column maps where they have the same schema name.

    Args:
        source (ColumnMap): loaded column that needs to be matched to the target columns
        target (List[ColumnMap]): columns loaded in the target sheet

        Note: these should both be specified in the dataset schema otherwise columns
        wont be matchable

    Returns:
        List: matched columns. 
    """
    # return [column for column in target if column.schema_column_name == source.schema_column_name]
    return [item for item in source if item.schema_column_name in [column.schema_column_name for column in target]]