from difflib import SequenceMatcher

import polars as pl

from config import settings

from ..common.list_matching import filter_list, match_list
from ..loaders.excel_loader import ExcelLoaderData
from ..loaders.helpers import match_excel_columns_to_schema
from ..models.base import (
    DynamicSheetMatching,
    ProcessValueMap,
    SchemaColumnMap,
    SchemaSheetMap,
)
from ..models.base_dataset import BaseDataset, DynamicDatasetSchema
from ..validators.base import BaseValidator, SeverityLevel, ValidationResult
from ..validators.data_validators import (
    CleaningLogToClean,
    ConsentCheck,
    CrossSheetIdCheck,
    CrossSheetRowSumCheck,
    DataTypeCheck,
    NaNDataCheck,
    PiiDataCheck,
    RawToCleanToLog,
    SurveyChoicesCheck,
    UniqueColumn,
)
from ..validators.schema_validators import (
    ColumnNameCheck,
    DuplicateSheetMatches,
    MandatoryColumns,
    MissingSheetsCheck,
    UnexpectedSheetsCheck,
)


class DynamicDataset(BaseDataset):
    """This aims to analyse an excel file and attepts to:
    - idenfity needed sheets, sheet types, sheet relationships
    - build a dataset schema
    - initialise the required validators

    This process focuses on sheets related to loops and non standardised datasets.
      Specifically:
    - possible parent/child clean_data sheets
    - possible parent/child raw_data sheets
    - possible parent/child cleaning_log sheets
    - other non standardised datasets

    Some sheets/columns that are always expected are still specified
      in DynamicDatasetSchema.

    If sheets and columns are named according to the minimum standards checklist
    then this process should have a reasonable chance of succeeding. The less
    the minimum standards checklist is followed, the more likely this process and
    the subsequent validation rules are to produce errors related to not
    finding required sheets or columns.

    Limitations:
    - loops within loops are currently not supported.

    """

    def __init__(self, data: ExcelLoaderData) -> None:
        self.data = data
        self.schema = DynamicDatasetSchema()
        self.sheet_matching: dict[str, DynamicSheetMatching] = {}
        self.validators: list[BaseValidator] = []

    def get_schema(self, *args, **kwargs) -> DynamicDatasetSchema:
        return self.schema

    def get_validators(self, *args, **kwargs) -> list[BaseValidator]:
        return self.validators

    def process_data(self) -> list[ValidationResult]:
        """Runs all the steps."""
        all_results: list[ValidationResult] = []

        results = self.match_data()
        if results:
            all_results.extend(results)

        results, consent_sheet = self.build_schema()
        if results:
            all_results.extend(results)

        # this must come after build_schema
        self.validators = [
            MissingSheetsCheck(schema=self.schema),
            UnexpectedSheetsCheck(),
            DuplicateSheetMatches(),
            MandatoryColumns(schema=self.schema),
            UniqueColumn(schema=self.schema),
            PiiDataCheck(schema=self.schema),
            ColumnNameCheck(),
        ]

        results = self.build_validators(consent_sheet)

        if results:
            all_results.extend(results)

        return all_results

    def build_validators(self, consent_sheet: str | None) -> list[ValidationResult]:
        """builds a list of validators matched to use the dynamically created schema.

        Current assumptions:
        - there is only ever one deletion log and it only lists deleted
          records for the parent object

        """
        results: list[ValidationResult] = []
        clean_sheets = [
            item for item, value in self.sheet_matching.items() if value.classification == "clean"
        ]
        cleaning_log_sheets = [
            item for item, value in self.sheet_matching.items() if value.log_type == "cleaning"
        ]
        raw_sheets = [
            item for item, value in self.sheet_matching.items() if value.classification == "raw"
        ]

        for sheet, details in self.sheet_matching.items():
            if details.linked_cleaning_log is not None:
                cleaning_log_sheet = details.linked_cleaning_log
            elif len(cleaning_log_sheets) == 1:
                cleaning_log_sheet = cleaning_log_sheets[0]
            else:
                cleaning_log_sheet = None

            if details.classification == "clean":
                if cleaning_log_sheet is not None:
                    self.validators.append(
                        CrossSheetIdCheck(
                            schema=self.schema,
                            master_sheet=sheet,
                            child_sheets=[cleaning_log_sheet],
                        )
                    )
                    self.validators.append(
                        CleaningLogToClean(
                            schema=self.schema,
                            cleaning_log_sheet=cleaning_log_sheet,
                            clean_data_sheet=sheet,
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            rule="DynamicDataset Creation build_validators",
                            message=f"No linked cleaning data sheet for the sheet"
                            f"'{sheet}' were found so the 'CleaningLogToClean' and"
                            "'CrossSheetIdCheck' rules could not be run.",
                            sheet_name=sheet,
                            severity=SeverityLevel.WARNING,
                        )
                    )

                if details.linked_raw_sheet is not None:
                    self.validators.append(
                        RawToCleanToLog(
                            schema=self.schema,
                            cleaning_log_sheet=cleaning_log_sheet,
                            clean_data_sheet=sheet,
                            raw_data_sheet=details.linked_raw_sheet,
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            rule="DynamicDataset Creation build_validators",
                            message=f"No linked raw sheet for the sheet '{sheet}' were"
                            "found so the 'RawToCleanToLog' rule could not be run.",
                            severity=SeverityLevel.WARNING,
                            sheet_name=sheet,
                        )
                    )

            elif details.classification == "raw":
                rowsum_sheets = []
                id_check_sheets = []
                clean_sheet = None
                master_deletion_log = None
                if details.linked_clean_sheet is not None:
                    rowsum_sheets.append(details.linked_clean_sheet)
                    id_check_sheets.append(details.linked_clean_sheet)
                    clean_sheet = self.sheet_matching[details.linked_clean_sheet]

                    if len(clean_sheets) == 1 or details.parent_sheet is None:
                        rowsum_sheets.append("deletion_log")
                    else:
                        master_deletion_log = "deletion_log"

                        self.validators.append(
                            CrossSheetRowSumCheck(
                                schema=self.schema,
                                master_sheet=sheet,
                                child_sheets=rowsum_sheets,
                                master_deletion_log=master_deletion_log,
                            )
                        )
                else:
                    results.append(
                        ValidationResult(
                            rule="DynamicDataset Creation build_validators",
                            message=f"No linked sheets for the raw data sheet '{sheet}'"
                            "were found so the 'CrossSheetRowSumCheck' rule could"
                            "not be run.",
                            severity=SeverityLevel.WARNING,
                            sheet_name=sheet,
                        )
                    )

                if clean_sheet is not None:
                    if details.parent_sheet is None:
                        id_check_sheets.append("deletion_log")
                    if cleaning_log_sheet is not None:
                        id_check_sheets.append(cleaning_log_sheet)

                    self.validators.append(
                        CrossSheetIdCheck(
                            schema=self.schema,
                            master_sheet=sheet,
                            child_sheets=id_check_sheets,
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            rule="DynamicDataset Creation build_validators",
                            message="No linked clean sheet for the raw data sheet"
                            f"'{sheet}' was found so the 'CrossSheetIdCheck' rule"
                            "could not be run.",
                            severity=SeverityLevel.WARNING,
                            sheet_name=sheet,
                        )
                    )

        if consent_sheet is not None:
            self.validators.append(
                ConsentCheck(
                    schema=self.schema,
                    raw_data_sheet=consent_sheet,
                    clean_data_sheet=self.sheet_matching[consent_sheet].linked_clean_sheet,
                )
            )
        else:
            results.append(
                ValidationResult(
                    rule="DynamicDataset Creation build_validators",
                    message="No possible sheet for 'consent' column was found.",
                    severity=SeverityLevel.WARNING,
                )
            )

        if clean_sheets:  # check unique
            self.validators.append(DataTypeCheck(schema=self.schema, check_sheets=clean_sheets))

            self.validators.append(
                SurveyChoicesCheck(schema=self.schema, check_sheets=clean_sheets)
            )
            self.validators.append(NaNDataCheck(schema=self.schema, check_sheets=clean_sheets))
        else:
            results.append(
                ValidationResult(
                    rule="DynamicDataset Creation build_validators",
                    message="No possible sheets for 'clean_data' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )

        if not raw_sheets:
            results.append(
                ValidationResult(
                    rule="DynamicDataset Creation build_validators",
                    message="No possible sheets for 'raw_data' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )
        if not cleaning_log_sheets:
            results.append(
                ValidationResult(
                    rule="DynamicDataset Creation build_validators",
                    message="No possible sheets for 'cleaning_log' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )

        return results

    def build_schema(self) -> tuple[list[ValidationResult], str | None]:
        """Builds a schema based on the matched dataset data."""
        consent_sheet = None
        results: list[ValidationResult] = []
        for sheet, details in self.sheet_matching.items():
            if details.classification in ["log", "clean", "raw"]:
                new_sheet = self.schema.add_loaded_sheet(
                    SchemaSheetMap(
                        standard_name=sheet,
                        parent_sheet=details.parent_sheet,
                        parent_linking_column=details.parent_linking_column,
                    )
                )

                if details.parent_linking_column is not None:
                    self.schema.add_mandatory_column_to_sheet(
                        sheet,
                        SchemaColumnMap(standard_name=details.parent_linking_column),
                    )

                if details.id_column is not None:
                    self.schema.add_mandatory_column_to_sheet(
                        sheet,
                        SchemaColumnMap(standard_name=details.id_column, is_unique=True),
                    )
                if details.parent_linking_column is not None:
                    self.schema.add_mandatory_column_to_sheet(
                        sheet,
                        SchemaColumnMap(standard_name=details.parent_linking_column),
                    )
                if details.classification == "raw":
                    if details.parent_sheet is None:
                        consent_sheet = sheet
                        self.schema.add_mandatory_column_to_sheet(
                            sheet,
                            SchemaColumnMap(
                                standard_name="consent",
                                alternate_names=[],
                                process_values=[
                                    ProcessValueMap(
                                        process_name="consent_check_validation",
                                        values=["yes"],
                                    )
                                ],
                            ),
                        )
                if details.log_type == "cleaning":
                    # parts of this may seem repetitive
                    # if there are multiple clean data sheets (from loops) and they
                    #  dont have their own cleaning log then its possible there will
                    #  be multiple id columns in cleaning data. this aims to make
                    #  sure that all likely id columns are in the schema
                    if details.log_id_column is not None:
                        self.schema.add_mandatory_column_to_sheet(
                            sheet, SchemaColumnMap(standard_name=details.log_id_column)
                        )

                    matches = match_list(settings.COMMON_ID_COLUMN_NAMES, details.data.columns)
                    matches = filter_list(matches, [details.log_id_column])
                    if len(matches) > 0:
                        for match in matches:
                            self.schema.add_mandatory_column_to_sheet(
                                sheet, SchemaColumnMap(standard_name=match)
                            )

                    for column in details.data.columns:
                        if (
                            "id" in column
                            and column not in matches
                            and column != details.log_id_column
                        ):
                            self.schema.add_mandatory_column_to_sheet(
                                sheet, SchemaColumnMap(standard_name=column)
                            )

                    self.schema.add_mandatory_column_to_sheet(
                        sheet, SchemaColumnMap(standard_name="old_value")
                    )
                    self.schema.add_mandatory_column_to_sheet(
                        sheet, SchemaColumnMap(standard_name="new_value")
                    )
                    self.schema.add_mandatory_column_to_sheet(
                        sheet,
                        SchemaColumnMap(
                            standard_name="question", alternate_names=["question_name"]
                        ),
                    )
                    self.schema.add_mandatory_column_to_sheet(
                        sheet,
                        SchemaColumnMap(
                            standard_name="change_type",
                            alternate_names=["changed"],
                            process_values=[
                                ProcessValueMap(
                                    process_name="cleaning_log_validation",
                                    values=["yes", "change_response", "blank_response"],
                                )
                            ],
                        ),
                    )
                new_sheet = self.schema.get_schema_loaded_sheet(sheet)
                assert new_sheet is not None  # added above
                result, column_map = match_excel_columns_to_schema(details.data.columns, new_sheet)
                if result is not None:
                    results.extend(result)

                if column_map:
                    self.data.set_column_map_for_loaded_sheet(sheet, column_map)
        return results, consent_sheet

    def match_data(self) -> list[ValidationResult]:
        """Attempts to identify and match sheets and columns required to build a
        schema and for validation rules.

        This process attempts to:
        - identify the type of sheet based on simple name matching. eg log, raw, clean
        - find a unique id column for the sheet, except cleaning log sheets
        - trys to link cleaning log sheets to clean data sheets
        - link parent and child sheets if there are loops
        - link raw data sheets to clean data sheets


        """
        results: list[ValidationResult] = []

        
        min_matching_score: float = 0.8
        name_scaler: float = 0.4
        overlap_scaler: float = 0.6
        # get schema sheet names and already matched excel sheet names
        expected_names = self.schema.get_all_sheet_names()
        expected_names.extend(self.data.get_loaded_sheet_excel_names())

        for sheet in self.data.loaded_sheets:
            if sheet.data_sheet_name.lower() in expected_names: 
                # dont need to process existing items that should have
                # been matched when loading the data
                continue

            self.sheet_matching[sheet.data_sheet_name] = DynamicSheetMatching(
                data=sheet.data,
                id_column=None,
                id_column_set=None,
                classification=None,
                log_type=None,
                parent_sheet=None,
            )

            # categorise the sheet based on simple name matching
            # deletion logs are part of the DynamicDatasetSchema already
            sheet_name_lower = sheet.data_sheet_name.lower()
            if any(
                term in sheet_name_lower for term in settings.CLEANING_LOG_SHEET_SEARCH_TERMS
            ) and any(term in sheet_name_lower for term in settings.CLEAN_DATA_SHEET_SEARCH_TERMS):
                self.sheet_matching[sheet.data_sheet_name].log_type = "cleaning"
                self.sheet_matching[sheet.data_sheet_name].classification = "log"
            elif any(term in sheet_name_lower for term in settings.CLEAN_DATA_SHEET_SEARCH_TERMS):
                self.sheet_matching[sheet.data_sheet_name].classification = "clean"
            elif any(term in sheet_name_lower for term in settings.RAW_DATA_SHEET_SEARCH_TERMS):
                self.sheet_matching[sheet.data_sheet_name].classification = "raw"
            else:
                self.sheet_matching[sheet.data_sheet_name].classification = "unknown"

            # try to find a unique column
            # store the set of unique values for later processing
            # some cleaning logs contain columns that could be unique but ignore these
            # as they probably wont be the columns needed for validation processes
            if self.sheet_matching[sheet.data_sheet_name].log_type != "cleaning":
                unique_col = self.find_unique_column(sheet.data)
                id_set = None
                if unique_col is not None:
                    id_set = set(sheet.data.select(unique_col).to_series().unique().to_list())
                    self.sheet_matching[sheet.data_sheet_name].id_column_set = id_set
                    self.sheet_matching[sheet.data_sheet_name].id_column = unique_col
                elif self.sheet_matching[sheet.data_sheet_name].classification != "unknown":
                    # only log this for sheets we are expecting an id for
                    results.append(
                        ValidationResult(
                            rule="DynamicDataset Creation",
                            message="No unique ID column was found for sheet"
                            f"'{sheet.data_sheet_name}'.",
                            severity=SeverityLevel.INFO,
                            sheet_name=sheet.data_sheet_name,
                        )
                    )
        cleaning_log_sheets = [
            k
            for k, v in self.sheet_matching.items()
            if v.classification == "log" and v.log_type == "cleaning"
        ]
        data_sheets = [k for k, v in self.sheet_matching.items() if v.classification != "log"]

        # try to  link the cleaning logs to another sheet
        for log_name in cleaning_log_sheets:
            log_sheet = self.sheet_matching[log_name]

            best_parent = None
            best_score = -1
            best_linking_log_column = None

            for data_name in data_sheets:
                data_sheet = self.sheet_matching[data_name]
                if data_sheet.id_column_set is None:
                    continue
                if data_sheet.id_column is None:
                    continue

                # find a linking column
                linking_log_column = None
                # look for a same name match
                if data_sheet.id_column in log_sheet.data.columns:
                    linking_log_column = data_sheet.id_column
                else:
                    alt_matches = []
                    # or a partial match
                    for column in log_sheet.data.columns:
                        if column in data_sheet.id_column:
                            alt_matches.append(column)

                    if len(alt_matches) == 1:
                        linking_log_column = alt_matches[0]
                    else:
                        # or a common name
                        matching_columns = match_list(
                            log_sheet.data.columns, settings.COMMON_ID_COLUMN_NAMES
                        )
                        if len(matching_columns) == 1:
                            linking_log_column = matching_columns[0]

                # compare names and overlapping id values
                if linking_log_column is not None:
                    name_sim = SequenceMatcher(None, log_name, data_name).ratio()

                    log_set = set(
                        log_sheet.data.select(linking_log_column).to_series().unique().to_list()
                    )
                    intersection = log_set.intersection(data_sheet.id_column_set)

                    if len(intersection) > 0:
                        overlap = len(intersection) / len(log_set)
                    else:
                        overlap = 0

                    combined_score = (name_sim * name_scaler) + (overlap * overlap_scaler)

                    if combined_score > best_score:
                        best_score = combined_score
                        best_parent = data_name
                        best_linking_log_column = linking_log_column
            # if there was a good enough score then assume its a parent
            if best_score > min_matching_score and best_parent is not None:
                if (
                    log_sheet.log_type == "cleaning"
                    and self.sheet_matching[best_parent].classification == "clean"
                ):
                    self.sheet_matching[best_parent].linked_cleaning_log = log_name
                    self.sheet_matching[log_name].log_id_column = best_linking_log_column

        raw_sheets = [k for k, v in self.sheet_matching.items() if v.classification == "raw"]
        clean_sheets = [k for k, v in self.sheet_matching.items() if v.classification == "clean"]

        self.match_child_parent(raw_sheets, self.sheet_matching)
        self.match_child_parent(clean_sheets, self.sheet_matching)

        # map raw data sheets to clean data sheets
        for clean_name in clean_sheets:
            clean_prof = self.sheet_matching[clean_name]
            if not clean_prof.id_column_set:
                continue

            best_raw = None
            best_score = -1

            for raw_name in raw_sheets:
                raw_prof = self.sheet_matching[raw_name]
                if not raw_prof.id_column_set:
                    continue

                # Score 1: Name similarity
                name_sim = SequenceMatcher(None, clean_name, raw_name).ratio()

                # Score 2: ID overlap (Clean IDs should be subset of Raw IDs)
                intersection = clean_prof.id_column_set.intersection(raw_prof.id_column_set)
                id_overlap = len(intersection) / len(clean_prof.id_column_set)

                # Combined score (weight name similarity higher)
                combined_score = (name_sim * name_scaler) + (id_overlap * overlap_scaler)

                if combined_score > best_score:
                    best_score = combined_score
                    best_raw = raw_name

            if best_score > min_matching_score:
                assert best_raw is not None
                self.sheet_matching[clean_name].linked_raw_sheet = best_raw
                self.sheet_matching[best_raw].linked_clean_sheet = clean_name

        unknown_sheets = [
            k for k, v in self.sheet_matching.items() if v.classification == "unknown"
        ]

        if unknown_sheets:
            self.data.unexpected_sheets = unknown_sheets
            for sheet in unknown_sheets:
                # dont perform additional validation of these sheets
                # they will have their own validation warning in
                # unexpected sheets validator
                self.data.remove_loaded_sheet(sheet)

        # check parent counts if loops. should only be one sheet without a parent
        clean_sheets = [
            item for item, value in self.sheet_matching.items() if value.classification == "clean"
        ]
        if len(clean_sheets) > 1:
            clean_parent_sheets = [
                item
                for item, value in self.sheet_matching.items()
                if value.classification == "clean" and value.parent_sheet is None
            ]
            if len(clean_parent_sheets) > 1:
                results.append(
                    ValidationResult(
                        rule="DynamicDataset Creation",
                        message=f"There are unmatched clean sheets. {len(clean_parent_sheets)}"
                        " clean data sheets did not match to a parent."
                        " There should only be 1 clean sheet without a parent.",
                        severity=SeverityLevel.ERROR,
                        details={"Unmatched clean sheets": clean_parent_sheets},
                    )
                )

        raw_sheets = [
            item for item, value in self.sheet_matching.items() if value.classification == "raw"
        ]

        if len(raw_sheets) > 1:
            raw_parent_sheets = [
                item
                for item, value in self.sheet_matching.items()
                if value.classification == "raw" and value.parent_sheet is None
            ]
            if len(raw_parent_sheets) > 1:
                results.append(
                    ValidationResult(
                        rule="DynamicDataset Creation",
                        message=f"There are unmatched raw sheets. {len(raw_parent_sheets)} raw data"
                        " sheets did not match to a parent."
                        " There should only be 1 raw sheet without a parent.",
                        severity=SeverityLevel.ERROR,
                        details={"Unmatched raw sheets": raw_parent_sheets},
                    )
                )

        results.append(
            ValidationResult(
                rule="DynamicDataset Creation",
                message="Sheet matching results.",
                severity=SeverityLevel.ADMIN_INFO,
                details=pl.DataFrame(
                    [
                        {
                            "key": key,
                            "id_column": m.id_column,
                            "classification": m.classification,
                            "log_type": m.log_type,
                            "parent": m.parent_sheet,
                            "parent_id_column": m.parent_linking_column,
                            "children": m.children,
                            "linked_cleaning_log": m.linked_cleaning_log,
                            "linked_raw_sheet": m.linked_raw_sheet,
                            "linked_clean_sheet": m.linked_clean_sheet,
                            "log_id_column": m.log_id_column,
                        }
                        for key, m in self.sheet_matching.items()
                    ]
                ).to_dict(),
            )
        )

        return results

    def match_child_parent(
        self, sheets: list[str], matched_sheets: dict[str, DynamicSheetMatching]
    ):
        """Attempt to match child parent sheets based on finding possible
        foreign keys between the sheets.


        """
        for child_name in sheets:
            child_prof = matched_sheets[child_name]
            if not child_prof.id_column_set:
                continue

            best_parent = None
            best_score = -1
            best_fk_col = None

            for parent_name in sheets:
                if parent_name == child_name:
                    continue
                parent_prof = matched_sheets[parent_name]
                if not parent_prof.id_column_set:
                    continue

                # Find FK column in child that matches parent's primary ID
                if parent_prof.id_column is not None:
                    linking_column = None
                    # try to find an exact column match
                    # if no match look for the parent column name in the
                    # child column names
                    if parent_prof.id_column in child_prof.data.columns:
                        linking_column = parent_prof.id_column
                    else:
                        alt_matches = []
                        for column in child_prof.data.columns:
                            if parent_prof.id_column in column:
                                alt_matches.append(column)

                        if len(alt_matches) == 1:
                            linking_column = alt_matches[0]

                    # see what the overlap of id values is
                    if linking_column is not None:
                        child_set = set(
                            child_prof.data.select(linking_column).to_series().unique().to_list()
                        )

                        intersection = child_set.intersection(parent_prof.id_column_set)
                        overlap_score = len(intersection) / len(child_set)

                        if overlap_score > best_score:
                            best_score = overlap_score
                            best_parent = parent_name
                            best_fk_col = linking_column

            if best_score > 0.8:
                assert best_parent is not None
                matched_sheets[child_name].parent_sheet = best_parent
                matched_sheets[child_name].parent_linking_column = best_fk_col
                matched_sheets[best_parent].children.append(child_name)

    def find_unique_column(self, df: pl.DataFrame):
        """Attempts to find a unique column in a dataframe

        Args:
            df (pl.DataFrame): dataframe to check

        Returns:
            _type_: return column if one match is found, otherwise None
        """
        unique_cols = []
        majority_unique_cols = []


        def _additional_matching(columns: list[str]):
            """Perform some additional checks to find possible unique columns"""
            matching_columns = match_list(columns, settings.COMMON_ID_COLUMN_NAMES)
            if len(matching_columns) == 1:
                return matching_columns[0]

            alt_matches = []
            # child sheets often have a unique column like person
            for column in columns:
                if "person" in column:
                    alt_matches.append(column)

            if len(alt_matches) == 1:
                return alt_matches[0]
            
            return None


        for col_name in df.columns:
            if col_name in settings.IGNORE_COLUMNS_FOR_VALIDATION:
                continue
            # Check if the number of unique values equals the total row count
            unique_count = df[col_name].n_unique()
            total_count = len(df)

            if unique_count == total_count:
                unique_cols.append(col_name)
            elif unique_count/total_count > 0.98: 
                # sometimes there can be a few duplicates 
                # (which there shouldnt and will cause validation errors later)
                # but still try to find the correct column if no unique ones are found
                majority_unique_cols.append(col_name)

        # some other columns, often from kobo, will show as unique
        # but these are not wanted
        # unique_cols = filter_list(unique_cols, settings.IGNORE_COLUMNS_FOR_VALIDATION)
        unique_cols_len = len(unique_cols)
        majority_unique_cols_len = len(majority_unique_cols)
        if unique_cols_len == 1:
            return unique_cols[0]
        elif unique_cols_len > 1:
            # try to match to common names if more than one match
            alt_match = _additional_matching(unique_cols)
            if alt_match is not None:
                return alt_match
        elif majority_unique_cols_len == 1:
            return majority_unique_cols[0]
        elif majority_unique_cols_len > 1:
            alt_match = _additional_matching(majority_unique_cols)
            if alt_match is not None:
                return alt_match

        return None
