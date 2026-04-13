from dataclasses import dataclass, field
from typing import Dict, List
from thefuzz import fuzz
from thefuzz import process

from config import settings

@dataclass
class FuzzMatch():
    standard_name: str
    matches: Dict= field(default_factory=dict) 


def match_list_to_list(source: List[str],
                        target: List[str],
                        fuzzy_match: bool,
                          fuzzy_match_limit: int = 2) -> tuple[list[str], List[FuzzMatch]]:
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

    literal_matches = match_list(source, target)
    fuzzy_matched_values: List[FuzzMatch] = []

    if fuzzy_match:
        # only do fuzzy match for a column if there was no literal match
        for search_item in filter_list(source, literal_matches):
            match_result = process.extractBests(query=search_item, 
                                              choices=target, 
                                              scorer= fuzz.WRatio,#settings.FUZZY_MATCH_SCORER,
                                              score_cutoff = settings.MIN_FUZZY_MATCH_SCORE,
                                              limit = fuzzy_match_limit)
            
            if match_result:
                details = FuzzMatch(standard_name=search_item)
                for match_item in match_result:
                    details.matches[match_item[0]] = match_item[1]
                
                fuzzy_matched_values.append(details)
    return literal_matches, fuzzy_matched_values
            
def match_list(source: List, target: List):
    """Returns items in source that are in target"""
    set_target = set(target)
    return [item for item in source if item in set_target]

def filter_list(source: List, target: List):
    """Returns items in source that are not in target"""
    set_target = set(target)  # this reduces the lookup time from O(n) to O(1)
    return [item for item in source if item not in set_target]

def combine_lists(source: List | None, target: List | None):
    """Combines two lists returning a unique list"""
    combined_list: List = []    

    if source is not None:
        combined_list.extend(source)
    
    if target is not None:
        combined_list.extend(target)

    return list(set(combined_list))

def add_to_list(source: str | None, target: List | None):
    """Adds item and list. returns a unique list."""
    combined_list: List = []    

    if source is not None:
        combined_list.append(source)

    if target is not None:
        combined_list.extend(target)

    return list(set(combined_list))

