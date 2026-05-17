from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from thefuzz import fuzz, process

from rqa_validator.config import settings

from ..loaders.base import DataColumnMap, DataSheetMap


@dataclass
class FuzzMatch:
    standard_name: str
    matches: dict = field(default_factory=dict)


def match_list_to_list(
    source: list[str],
    target: list[str],
    fuzzy_match: bool,
    fuzzy_match_limit: int = 2,
    lower_values: bool = True,
) -> tuple[list[str], list[FuzzMatch]]:
    """Checks if items in a source list are found in a target list.
        Optionally performs fuzzy matching on columns in the source
        list if there was no literal match found with items in the target
        list.

    Args:
        source (List[str]): list of items to search for
        targets (List[str]): list of items to search against
        fuzzy_match (bool): if fuzzy matching should be performed
        fuzzy_match_limit (int, optional): Max number of fuzzy matches to return.
            Defaults to 2.

    Returns:
        tuple[list[str], List[FuzzMatch]: a list of literal matches,
                                            a list of fuzzy matches.
    """

    if lower_values:
        l_source = list(map(str.lower, source))
        l_target = list(map(str.lower, target))
    else:
        l_source = source
        l_target = target

    literal_matches = match_list(l_source, l_target)
    fuzzy_matched_values: list[FuzzMatch] = []

    if fuzzy_match:
        # only do fuzzy match for a column if there was no literal match
        for search_item in filter_list(l_source, literal_matches):
            # check if the items have a similar length
            l_target_tolerance = filter_list_with_tolerance(search_item, l_target)

            if l_target_tolerance:
                match_result = process.extractBests(
                    query=search_item,
                    choices=l_target_tolerance,
                    scorer=fuzz.WRatio,  # settings.FUZZY_MATCH_SCORER,
                    score_cutoff=settings.MIN_FUZZY_MATCH_SCORE,
                    limit=fuzzy_match_limit,
                )

                if match_result:
                    details = FuzzMatch(standard_name=search_item)
                    for match_item in match_result:
                        details.matches[match_item[0]] = match_item[1]

                    fuzzy_matched_values.append(details)
    return literal_matches, fuzzy_matched_values


def match_list(source: list, target: list) -> list:
    """Returns items in source that are in target"""
    set_target = set(target)
    return [item for item in source if item in set_target]


def unique_list(source: list) -> list[Any]:
    """returns a list of unique items"""
    return list(set(source))


def filter_list(source: list, target: list) -> list:
    """Returns items in source that are not in target"""
    set_target = set(target)
    return [item for item in source if item not in set_target]


def filter_list_with_tolerance(
    source: str,
    target: list[str],
    tolerance_ratio: float = settings.FUZZY_MATCH_STRING_LENGTH_RATIO,
) -> list[str]:
    """Filters a list based on a comparison between the string length
    of source and items in a target list using a tolerance factor.

    So strings of a similar enough length will be returned but if the length
    difference is too great then they will not be returned."""

    def _check_length_tolerance(search_item: str, target_item: str):
        length_search_item = len(search_item)
        length_target_item = len(target_item)

        ratio = min(length_target_item, length_search_item) / max(
            length_target_item, length_search_item
        )

        return ratio >= tolerance_ratio

    return [item for item in target if _check_length_tolerance(source, item)]


def duplicate_list_items(source: list) -> list[Any]:
    """returns a list of items that appear in a list multiple times.

    Args:
        source (List): list of items to check

    Returns:
        list[Any]: list of duplicated items. should be unique list.
    """
    item_counts = Counter(source)
    return [item for item in set(source) if item_counts[item] > 1]


def combine_lists(source: list | None, target: list | None, unique_list: bool = True):
    """Combines two lists returning a unique list"""
    combined_list: list = []

    if source is not None:
        combined_list.extend(source)

    if target is not None:
        combined_list.extend(target)

    if unique_list:
        return list(set(combined_list))
    else:
        return combined_list


def add_to_list(item: str | None, target: list | None) -> list:
    """Adds item and list. returns a unique list."""
    combined_list: list = []

    if item is not None:
        combined_list.append(item)

    if target is not None:
        combined_list.extend(target)

    return list(set(combined_list))


def is_in_list(item: str, target: list) -> bool:
    """Checks if an item is in a list"""
    return item in target


def match_sheet_columns(
    source: list[DataColumnMap], target: list[DataColumnMap]
) -> list[tuple[DataColumnMap, DataColumnMap]]:
    """matches columns between two column maps where they have the same schema name.

    Args:
        source (ColumnMap): loaded column that needs to be matched to the target columns
        target (List[ColumnMap]): columns loaded in the target sheet

        Note: these should both be specified in the dataset schema otherwise columns
        wont be matchable

    Returns:
        List[tuple[DataColumnMap, DataColumnMap]]:matched columns from source and target
    """

    target_names = {col.schema_column_name: col for col in target}

    matches: list[tuple[DataColumnMap, DataColumnMap]] = []
    for s_item in source:
        if s_item.schema_column_name in target_names:
            t_item = target_names[s_item.schema_column_name]
            matches.append((s_item, t_item))

    return matches


def match_sheet_columns_ids(
    source: list[DataColumnMap], target: list[DataColumnMap]
) -> tuple[list[DataColumnMap], list[DataColumnMap]]:
    """A very simple way to try and find id columns that match between two column lists.
      Attempts to find columns that are the same as commonly used id column names.
      If one match is found for both using this assumes that the two datasets are
      linkable through these columns

       This process should be used as a last resort after attempting to directly
        match the columns using other processes.

    Args:
        source (List[DataColumnMap]): list of columns from a soruce dataset
        target (List[DataColumnMap]): list of columns from a target dataset

    Returns:
        tuple[list[DataColumnMap], list[DataColumnMap]]: filtered source and
        target datasets
    """
    source_len = len(source)
    target_len = len(target)
    filtered_source = []
    filtered_target = []
    common_id_set = set(settings.COMMON_ID_COLUMN_NAMES)

    if source_len > 1:
        filtered_source = [item for item in source if item.data_column_name in common_id_set]
    elif source_len == 1:
        filtered_source = source
    if target_len > 1:
        filtered_target = [item for item in target if item.data_column_name in common_id_set]
    elif target_len == 1:
        filtered_target = target

    return filtered_source, filtered_target


def filter_loaded_sheets(
    sheets: list[str], loaded_sheets: dict[str, DataSheetMap]
) -> dict[str, DataSheetMap]:
    """Filters a DataSheetMap dict by the sheets

    Args:
        sheets (List[str]): sheets to be ratained from loaded_sheets
        loaded_sheets (dict[str, DataSheetMap]): data loaded sheets

    Returns:
        Dict[str, DataSheetMap]: filtered dict of loaded data sheets
    """
    return {key: loaded_sheets[key] for key in sheets}


def get_set_overlap(source_data: set, target_data: set) -> float:
    """Gets the overlap of two sets by calculating the intersection \
     of both sets

    Args:
        source_data (set): set of source data
        target_data (set): set of target data

    Returns:
        float: overlap 
    """
    intersection = source_data.intersection(target_data)

    if len(intersection) > 0:
        overlap = len(intersection) / len(source_data)
    else:
        overlap = 0.0

    return overlap
