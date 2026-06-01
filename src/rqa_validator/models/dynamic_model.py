from rqa_validator.models.base_dataset import DynamicDatasetSchema


from rqa_validator.loaders.excel_loader import ExcelLoaderData


from difflib import SequenceMatcher
from typing import Any

import polars as pl

from rqa_validator.config import settings

from ..common.list_matching import filter_list, get_set_overlap, match_list, unique_list
from ..loaders.base_excel_loader import BaseExcelLoader
from ..loaders.excel_loader import ExcelLoaderData
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
        self.data: ExcelLoaderData = data
        self.schema: DynamicDatasetSchema = DynamicDatasetSchema()
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
        rule = "DynamicSchemaCreation_build_validators"
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
                            rule=rule,
                            message=f"No linked cleaning log data sheet for the sheet"
                            f" '{sheet}' was found so the 'CleaningLogToClean' and"
                            " 'CrossSheetIdCheck' rules could not be run.",
                            sheet_name=sheet,
                            severity=SeverityLevel.ERROR,
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
                            rule=rule,
                            message=f"No linked raw sheet for the sheet '{sheet}' was"
                            " found so the 'RawToCleanToLog' rule could not be run.",
                            severity=SeverityLevel.ERROR,
                            sheet_name=sheet,
                        )
                    )
                if details.parent_sheet is not None:
                    self.validators.append(
                        CrossSheetIdCheck(
                            schema=self.schema,
                            master_sheet=details.parent_sheet,
                            child_sheets=[sheet],
                        )
                    )

            elif details.classification == "raw":
                rowsum_sheets: list[str] = []
                id_check_sheets: list[str] = []
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
                            rule=rule,
                            message=f"No linked sheets for the raw data sheet '{sheet}'"
                            " was found so the 'CrossSheetRowSumCheck' rule could"
                            " not be run.",
                            severity=SeverityLevel.ERROR,
                            sheet_name=sheet,
                        )
                    )

                if details.parent_sheet is not None:
                    self.validators.append(
                        CrossSheetIdCheck(
                            schema=self.schema,
                            master_sheet=details.parent_sheet,
                            child_sheets=[sheet],
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
                            rule=rule,
                            message="No linked clean sheet for the raw data sheet"
                            f" '{sheet}' was found so the 'CrossSheetIdCheck' rule"
                            " could not be run.",
                            severity=SeverityLevel.ERROR,
                            sheet_name=sheet,
                        )
                    )

        if consent_sheet is not None:
            consent_linked_clean_sheet = self.sheet_matching[consent_sheet].linked_clean_sheet
            if consent_linked_clean_sheet is None:
                results.append(
                    ValidationResult(
                        rule=rule,
                        message="No linked clean sheet for the raw data sheet"
                        f" '{consent_sheet}' was found so the 'ConsentCheck' rule"
                        " could not be run.",
                        severity=SeverityLevel.ERROR,
                        sheet_name=consent_sheet,
                    )
                )
            else:
                self.validators.append(
                    ConsentCheck(
                        schema=self.schema,
                        raw_data_sheet=consent_sheet,
                        clean_data_sheet=consent_linked_clean_sheet,
                    )
                )
        else:
            results.append(
                ValidationResult(
                    rule=rule,
                    message="No possible sheet for 'consent' column was found.",
                    severity=SeverityLevel.ERROR,
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
                    rule=rule,
                    message="No possible sheets for 'clean_data' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )

        if not raw_sheets:
            results.append(
                ValidationResult(
                    rule=rule,
                    message="No possible sheets for 'raw_data' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )
        if not cleaning_log_sheets:
            results.append(
                ValidationResult(
                    rule=rule,
                    message="No possible sheets for 'cleaning_log' were found.",
                    severity=SeverityLevel.ERROR,
                )
            )

        return results

    def build_schema(self) -> tuple[list[ValidationResult], str | None]:
        """Builds a schema based on the matched dataset data."""
        consent_sheet = None
        loader = BaseExcelLoader()
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

                # in the rare case that a child sheet only has at most one record for each parent
                # then the id column found could accidentially also be the foreign key column
                # i dont think this matters as far as the validation goes(?) but it should
                # be the first column created so that the unique flag is set
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
                                        values=["yes", "oui"],
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
                result, column_map = loader.match_excel_columns_to_schema(
                    details.data.columns, new_sheet
                )
                if result:
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
        rule = "DynamicSchemaCreation_match_data"

        min_matching_score: float = 0.8
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
                unique_columns: list[str] = self._find_unique_column(sheet.data)
                if len(unique_columns) == 1:
                    id_set: set[Any] = set[Any](
                        sheet.data.select(unique_columns[0]).to_series().unique().to_list()
                    )
                    self.sheet_matching[sheet.data_sheet_name].id_column_set = id_set
                    self.sheet_matching[sheet.data_sheet_name].id_column = unique_columns[0]
                elif self.sheet_matching[sheet.data_sheet_name].classification != "unknown":
                    # only log this for sheets we are expecting an id for
                    results.append(
                        ValidationResult(
                            rule=rule,
                            message="Expected one unique ID column for sheet"
                            f" '{sheet.data_sheet_name}' but {len(unique_columns)} were found.",
                            severity=SeverityLevel.ERROR,
                            sheet_name=sheet.data_sheet_name,
                            details={"unique_columns": unique_columns},
                        )
                    )
        cleaning_log_sheets = [
            k
            for k, v in self.sheet_matching.items()
            if v.classification == "log" and v.log_type == "cleaning"
        ]
        clean_sheets: list[str] = [
            k for k, v in self.sheet_matching.items() if v.classification == "clean"
        ]
        raw_sheets: list[str] = [
            k for k, v in self.sheet_matching.items() if v.classification == "raw"
        ]

        # try to  link the cleaning logs to another sheet
        for log_sheet in cleaning_log_sheets:
            match_log_sheet = self.sheet_matching[log_sheet]

            best_parent = None
            best_score = -1
            best_linking_log_column = None

            for clean_sheet in clean_sheets:
                match_clean_sheet = self.sheet_matching[clean_sheet]
                if match_clean_sheet.id_column_set is None:
                    continue
                if match_clean_sheet.id_column is None:
                    continue

                # find a linking column
                linking_log_columns = self._find_linking_column(
                    match_log_sheet.data.columns, match_clean_sheet.id_column, True
                )
                # compare names and overlapping id values
                if linking_log_columns:
                    for linking_log_column in linking_log_columns:
                        log_set = set(
                            match_log_sheet.data.select(linking_log_column)
                            .to_series()
                            .unique()
                            .to_list()
                        )
                        combined_score = self._get_similarity_score(
                            log_sheet, log_set, clean_sheet, match_clean_sheet.id_column_set
                        )

                        if combined_score > best_score:
                            best_score = combined_score
                            best_parent = clean_sheet
                            best_linking_log_column = linking_log_column
            # if there was a good enough score then assume its a parent
            if best_score > min_matching_score and best_parent is not None:
                self.sheet_matching[best_parent].linked_cleaning_log = log_sheet
                self.sheet_matching[log_sheet].log_id_column = best_linking_log_column

        self._match_child_parent(raw_sheets)
        self._match_child_parent(clean_sheets)

        # map raw data sheets to clean data sheets
        for clean_sheet in clean_sheets:
            match_clean_sheet = self.sheet_matching[clean_sheet]
            if not match_clean_sheet.id_column_set:
                continue

            best_raw = None
            best_score = -1

            for raw_sheet in raw_sheets:
                match_raw_sheet = self.sheet_matching[raw_sheet]
                if not match_raw_sheet.id_column_set:
                    continue

                combined_score = self._get_similarity_score(
                    clean_sheet,
                    match_clean_sheet.id_column_set,
                    raw_sheet,
                    match_raw_sheet.id_column_set,
                )

                if combined_score > best_score:
                    best_score = combined_score
                    best_raw = raw_sheet

            if best_score > min_matching_score:
                assert best_raw is not None
                self.sheet_matching[clean_sheet].linked_raw_sheet = best_raw
                self.sheet_matching[best_raw].linked_clean_sheet = clean_sheet

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
        if len(clean_sheets) > 1:
            clean_parent_sheets = [
                item
                for item, value in self.sheet_matching.items()
                if value.classification == "clean" and value.parent_sheet is None
            ]
            if len(clean_parent_sheets) > 1:
                results.append(
                    ValidationResult(
                        rule=rule,
                        message=f"{len(clean_parent_sheets)} clean data sheets did not match to a"
                        " parent. There should only be 1 clean data sheet without a parent.",
                        severity=SeverityLevel.ERROR,
                        details={"Unmatched clean data sheets": clean_parent_sheets},
                    )
                )

        if len(raw_sheets) > 1:
            raw_parent_sheets = [
                item
                for item, value in self.sheet_matching.items()
                if value.classification == "raw" and value.parent_sheet is None
            ]
            if len(raw_parent_sheets) > 1:
                results.append(
                    ValidationResult(
                        rule=rule,
                        message=f"{len(raw_parent_sheets)} raw data sheets did not match to a"
                        " parent. There should only be 1 raw data sheet without a parent.",
                        severity=SeverityLevel.ERROR,
                        details={"Unmatched raw data sheets": raw_parent_sheets},
                    )
                )

        results.append(
            ValidationResult(
                rule=rule,
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

    def _get_similarity_score(
        self,
        source_name: str,
        source_data: set[Any],
        target_name: str,
        target_data: set[Any],
        name_scaler: float = 0.4,
        overlap_scaler: float = 0.6,
    ) -> float:
        """Calculates the similarity between two objects. This could be either
        - two columns and their names or
        - two sheet names and their id columns
        This is done by calculating the similarity of their names and the
        intersection of their id columns and then applying some weights
        to the results.

        Args:
            source_name (str): name of the source item. either a column or sheet name
            source_data (set): the set of source id column values
            target_name (str): name of the target item. either a column or sheet name
            target_data (set): the set of target id column values
            name_scaler (float, optional): weight applied to name. Defaults to 0.4.
            overlap_scaler (float, optional): weight applied to overlap. Defaults to 0.6.

        Returns:
            float: similarity score.
        """
        name_similarity = SequenceMatcher(None, source_name, target_name).ratio()
        overlap = get_set_overlap(source_data, target_data)
        return (name_similarity * name_scaler) + (overlap * overlap_scaler)

    def _find_linking_column(
        self, child_columns: list[str], parent_id_column: str, allow_common_names: bool = False
    ) -> list[str]:
        """Attempts to find name matches between a parent id column and a list of
               child columns.

               Optionaly also checks a list of common names if no match was found.

        Args:
            child_columns (list[str]): list of child columns to search
            parent_id_column (str): name of parent column
            allow_common_names (bool, optional): Option to check for common names.
                Defaults to False.

        Returns:
            list[str] : returns possible name matches if found
        """
        possible_columns: list[str] = []
        #  Exact match
        if parent_id_column in child_columns:
            possible_columns.append(parent_id_column)
            # return parent_id_col

        # Partial match
        alt_matches = [column for column in child_columns if parent_id_column in column]
        if alt_matches:
            possible_columns.extend(alt_matches)

        # check common names
        if allow_common_names:
            matching_columns: list[str] = match_list(child_columns, settings.COMMON_ID_COLUMN_NAMES)
            if matching_columns:
                possible_columns.extend(matching_columns)

        if possible_columns:
            possible_columns = unique_list(possible_columns)

        return possible_columns

    def _match_child_parent(self, sheets: list[str]):
        """Attempt to match child parent sheets based on finding possible
        foreign keys between the sheets.

        No name matching is done for this process as the names are likely
        to be very different between child and parent sheets.
        """
        for child_sheet in sheets:
            child_match_sheet = self.sheet_matching[child_sheet]
            if not child_match_sheet.id_column_set:
                continue

            best_parent = None
            best_score = -1
            best_fk_column = None

            for parent_sheet in sheets:
                if parent_sheet == child_sheet:
                    continue
                parent_match_sheet = self.sheet_matching[parent_sheet]
                if not parent_match_sheet.id_column_set:
                    continue

                # Find FK column in child that matches parent's primary ID
                if parent_match_sheet.id_column is not None:
                    # try to find an id column match
                    linking_columns = self._find_linking_column(
                        child_match_sheet.data.columns, parent_match_sheet.id_column
                    )
                    # see what the overlap of id values is
                    if linking_columns:
                        for linking_column in linking_columns:
                            child_set = set(
                                child_match_sheet.data.select(linking_column)
                                .to_series()
                                .unique()
                                .to_list()
                            )
                            overlap = get_set_overlap(child_set, parent_match_sheet.id_column_set)

                            if overlap > best_score:
                                best_score = overlap
                                best_parent = parent_sheet
                                best_fk_column = linking_column

            if best_score > 0.8:
                assert best_parent is not None
                self.sheet_matching[child_sheet].parent_sheet = best_parent
                self.sheet_matching[child_sheet].parent_linking_column = best_fk_column
                self.sheet_matching[best_parent].children.append(child_sheet)

    def _find_unique_column(self, data: pl.DataFrame) -> list[str]:
        """Attempts to find unique columns in a dataframe

        Args:
            data (pl.DataFrame): dataframe to check

        Returns:
            list[str] : returns unique columns if found
        """
        unique_columns: list[str] = []
        majority_unique_columns: list[str] = []

        def _additional_matching(columns: list[str]) -> list[str]:
            """Perform some additional checks to find possible unique columns"""
            matching_columns: list[str] = match_list(columns, settings.COMMON_ID_COLUMN_NAMES)
            if len(matching_columns) == 1:
                return matching_columns

            # look for modified columns from ID_FILTER_NAMES that are often renamed
            # that should be ignored
            filter_columns = [
                item for item in columns if any(term in item for term in settings.ID_FILTER_NAMES)
            ]
            matching_columns = filter_list(columns, filter_columns)
            if len(matching_columns) == 1:
                return matching_columns

            # child sheets often have a unique column like person
            matching_columns = [column for column in columns if "person" in column]
            if len(matching_columns) == 1:
                return matching_columns

            return matching_columns

        for column in data.columns:
            if column in settings.IGNORE_COLUMNS_FOR_VALIDATION:
                # some other columns, often from kobo, will show as unique
                # but these are not wanted
                continue
            # Check if the number of unique values equals the total row count
            unique_count = data[column].n_unique()
            total_count = len(data)

            if unique_count == total_count:
                unique_columns.append(column)
            elif unique_count / total_count > 0.95:
                # sometimes there can be a few duplicates
                # (which there shouldnt and will cause validation errors later)
                # but still try to find the correct column if no unique ones are found
                majority_unique_columns.append(column)

        unique_columns_len = len(unique_columns)
        majority_unique_columns_len = len(majority_unique_columns)
        if unique_columns_len == 1:
            return unique_columns
        elif unique_columns_len > 1:
            # try to match to common names if more than one match
            alt_match = _additional_matching(unique_columns)
            if alt_match:
                return alt_match
        elif majority_unique_columns_len == 1:
            return majority_unique_columns
        elif majority_unique_columns_len > 1:
            alt_match = _additional_matching(majority_unique_columns)
            if alt_match:
                return alt_match

        return unique_columns
