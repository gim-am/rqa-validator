from ...common.file_export import df_to_csv
from ...common.list_matching import filter_list
from ...common.expression_builder import create_column_difference_expression
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ..base import BaseValidator, ValidationResult, SeverityLevel
from ..helpers import (
    get_data_loaded_columns,
    get_data_loaded_sheets,
    get_data_sheet_ids,
    get_matching_id_columns,
    get_matching_id_columns_alt,
    get_schema_loaded_sheets,
    get_schema_process_value,
)


import polars as pl





class CleaningLogToClean(BaseValidator):
    """This process validates the data in the cleaning log

    After making sure that the required sheets and columns have been loaded and matched
    the process validates that all the items in a cleaning log are reflected in the clean data.

    The output includes:
    - items in cleaning log that have multiple updates for the same question
    - questions in cleaning log that are not present in clean_data
    - items where there is a difference between cleaning_log and clean_data values

    """

    def __init__(
        self,
        schema: BaseDatasetSchema,
        clean_data_sheet: str = "clean_data",
        cleaning_log_sheet: str = "cleaning_log",
        cleaning_log_new_value_column: str = "new_value",
        cleaning_log_old_value_column: str = "old_value",
        cleaning_log_question_column: str = "question",
        cleaning_log_change_type_column: str = "change_type",
    ) -> None:
        """Validates that the items in a cleaning log are reflected in the clean data

        Args:
            schema (BaseDatasetSchema): dataset schema for the dataset
            clean_data_sheet (str, optional): name of the clean data sheet. Defaults to 'clean_data'.
            cleaning_log_sheet (str, optional): name of the cleaning log sheet. Defaults to 'cleaning_log'.
            cleaning_log_new_value_column (str, optional): name of the cleaning log new value column. Defaults to 'new_value'.
            cleaning_log_old_value_column (str, optional): name of the cleaning log old value column. Defaults to 'old_value'.
            cleaning_log_question_column (str, optional): name of the cleaning log quesitons column. Defaults to 'question'.
            cleaning_log_change_type_column (str, optional): name of the cleaning log change_type column. Defaults to 'change_type'
        """
        self.schema = schema
        self.clean_data_sheet = clean_data_sheet
        self.cleaning_log_sheet = cleaning_log_sheet
        self.cleaning_log_new_value_column = cleaning_log_new_value_column
        self.cleaning_log_old_value_column = cleaning_log_old_value_column
        self.cleaning_log_question_column = cleaning_log_question_column
        self.cleaning_log_change_type_column = cleaning_log_change_type_column
        # the ProcessValueMap that contains the list of possible values needed in cleaning_log_change_type_column
        self.process_value_map_name = "cleaning_log_validation"

    @property
    def name(self) -> str:
        return "CleaningLogToClean"

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """This process validates the data in the cleaning log

        After making sure that the required sheets and columns have been loaded and matched
        the process validates that all the items in a cleaning log are reflected in the clean data.


        The output includes:
        - items in cleaning log that have multiple updates for the same question
        - questions in cleaning log that are not present in clean_data
        - items where there is a difference between cleaning_log and clean_data values

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []

        multiple_changes_filename = "cleaning_log_validation_multiple_changes"
        validation_results_filename = "cleaning_log_validation_results"

        # PRE-VALIDATION - check sheets, columns etc all exist

        result, data_loaded_sheets = get_data_loaded_sheets(
            data=data,
            sheet_names=[self.clean_data_sheet, self.cleaning_log_sheet],
            rule=self.name,
        )

        if result:
            results.extend(result)
            return results

        result, schema_loaded_sheets = get_schema_loaded_sheets(
            schema=self.schema, sheet_names=[self.cleaning_log_sheet], rule=self.name
        )

        if result:
            results.extend(result)
            return results

        result, data_sheet_ids = get_data_sheet_ids(
            schema=self.schema,
            data={self.clean_data_sheet: data_loaded_sheets[self.clean_data_sheet]},
            rule=self.name,
        )

        if result:
            results.extend(result)
            return results

        result, clean_to_log_matching_id_columns = get_matching_id_columns(
            data_sheet_ids[self.clean_data_sheet],
            self.clean_data_sheet,
            data_loaded_sheets[self.cleaning_log_sheet].column_map,
            self.cleaning_log_sheet,
            self.name,
        )
        if result is not None:
            result, clean_data_id_columns, clean_log_id_columns = (
                get_matching_id_columns_alt(
                    data_sheet_ids[self.clean_data_sheet],
                    self.clean_data_sheet,
                    data_loaded_sheets[self.cleaning_log_sheet].column_map,
                    self.cleaning_log_sheet,
                    self.name,
                )
            )
            if result is not None:
                results.append(result)
                return results
            else:
                clean_data_id_columns = clean_data_id_columns[0]
                clean_log_id_columns = clean_log_id_columns[0]
        else:
            clean_data_id_columns = clean_to_log_matching_id_columns[0][0]
            clean_log_id_columns = clean_to_log_matching_id_columns[0][1]

        result, data_loaded_columns = get_data_loaded_columns(
            data={
                self.cleaning_log_new_value_column: data_loaded_sheets[
                    self.cleaning_log_sheet
                ],
                self.cleaning_log_old_value_column: data_loaded_sheets[
                    self.cleaning_log_sheet
                ],
                self.cleaning_log_question_column: data_loaded_sheets[
                    self.cleaning_log_sheet
                ],
                self.cleaning_log_change_type_column: data_loaded_sheets[
                    self.cleaning_log_sheet
                ],
                #   clean_log_id_columns.schema_column_name: data_loaded_sheets[self.cleaning_log_sheet],
            },
            rule=self.name,
        )

        if result:
            results.extend(result)
            return results

        schema_change_type_column = schema_loaded_sheets[
            self.cleaning_log_sheet
        ].get_column(self.cleaning_log_change_type_column)
        if schema_change_type_column is None:
            # this should already have been validated when checking mandatory columns
            return results

        result, schema_change_type_values = get_schema_process_value(
            self.process_value_map_name,
            self.cleaning_log_sheet,
            schema_change_type_column,
            self.name,
        )
        if result is not None:
            results.append(result)
            return results

        assert schema_change_type_values is not None

        # TRANSFORMATION: transforms data in preparation for comparison
        # dataframe of actual changes made
        modified_rows_df = (
            data_loaded_sheets[self.cleaning_log_sheet]
            .data.filter(
                pl.col(
                    data_loaded_columns[
                        self.cleaning_log_change_type_column
                    ].data_column_name
                )
                .str.to_lowercase()
                .is_in(schema_change_type_values.values)
            )
            .filter(
                (
                    pl.col(clean_log_id_columns.data_column_name)
                    .cast(pl.Utf8)
                    .str.strip_chars(" ")
                    .is_not_null()
                )
                & (
                    pl.col(clean_log_id_columns.data_column_name)
                    .cast(pl.Utf8)
                    .str.strip_chars(" ")
                    != ""
                )
            )
            .select(
                [
                    clean_log_id_columns.data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_new_value_column
                    ].data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_old_value_column
                    ].data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_change_type_column
                    ].data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_question_column
                    ].data_column_name,
                ]
            )
        )

        # Compares the cleaning log to clean_data

        # racods where the same question was updated more than once for the same id
        multiple_change_mask = modified_rows_df.select(
            clean_log_id_columns.data_column_name,
            data_loaded_columns[self.cleaning_log_question_column].data_column_name,
        ).is_duplicated()

        multiple_change_df = modified_rows_df.filter(multiple_change_mask).sort(
            clean_log_id_columns.data_column_name
        )

        if multiple_change_df.height > 0:
            df_to_csv(data=multiple_change_df, filename=multiple_changes_filename)
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"{
                        multiple_change_df.select(
                            clean_log_id_columns.data_column_name
                        ).n_unique()
                    } Ids had multiple changes for the same question. \
                            These were not validated. Check the output file {
                        multiple_changes_filename
                    } for details.",
                    severity=SeverityLevel.WARNING,
                    details=multiple_change_df.to_dict(),
                )
            )

        # scan cleaning log for old value = new value
        same_value_df = modified_rows_df.filter(
            pl.col(
                data_loaded_columns[self.cleaning_log_new_value_column].data_column_name
            ).cast(pl.Utf8)
            == pl.col(
                data_loaded_columns[self.cleaning_log_old_value_column].data_column_name
            ).cast(pl.Utf8)
        ).select(
            clean_log_id_columns.data_column_name,
            data_loaded_columns[self.cleaning_log_new_value_column].data_column_name,
            data_loaded_columns[self.cleaning_log_old_value_column].data_column_name,
            data_loaded_columns[self.cleaning_log_change_type_column].data_column_name,
        )
        if same_value_df.height > 0:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"{same_value_df.height} row/s had {data_loaded_columns[self.cleaning_log_old_value_column].data_column_name} equal {data_loaded_columns[self.cleaning_log_new_value_column].data_column_name}. Check the output file {multiple_changes_filename} for details.",
                    severity=SeverityLevel.WARNING,
                    details=same_value_df.to_dict(),
                )
            )

        # remove records with multiple chages as there is no way to determine which should
        # be the most recent
        # also remove other columns as they are no longer necessary
        unique_modified_rows_df = (
            modified_rows_df.filter(~multiple_change_mask)
            .sort(clean_log_id_columns.data_column_name)
            .select(
                [
                    clean_log_id_columns.data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_new_value_column
                    ].data_column_name,
                    data_loaded_columns[
                        self.cleaning_log_question_column
                    ].data_column_name,
                ]
            )
        )

        if unique_modified_rows_df.height < 1:
            return results
        # get a list of questions that had values changed
        questions = (
            unique_modified_rows_df.select(
                data_loaded_columns[self.cleaning_log_question_column].data_column_name
            )
            .unique()
            .to_series()
            .str.to_lowercase()
            .to_list()
        )

        missing_quesitons = filter_list(
            questions, data_loaded_sheets[self.clean_data_sheet].data.columns
        )
        if missing_quesitons:
            results.append(
                ValidationResult(
                    rule=self.name,
                    message=f"There are questions listed in {data_loaded_sheets[self.cleaning_log_sheet].data_sheet_name} that were not found in {data_loaded_sheets[self.clean_data_sheet].data_sheet_name}. See output for details.",
                    severity=SeverityLevel.WARNING,
                    details={"missing_questions": missing_quesitons},
                )
            )
            questions = filter_list(questions, missing_quesitons)
            if len(questions) < 1:
                # if no valid questions left to check
                return results

        # add column to specifiy an update. this helps to specify which
        # questions were updated later after the pivot as the pivot will
        # add a column for each question even if that question was not updated
        # for a particular uuid.
        # The result of this will be that question columns
        # that actually had an update in cleaning log will have 'true' for that question
        # while all other other questions will be null
        # fill null with '' to make comparison easier later
        unique_modified_rows_df = unique_modified_rows_df.with_columns(
            pl.lit(True).alias("is_update")
        ).with_columns(
            pl.col(
                data_loaded_columns[self.cleaning_log_new_value_column].data_column_name
            )
        )  # .fill_null(''))

        # pivot the table for use later. lower the questions/column names.
        unique_modified_rows_df = unique_modified_rows_df.pivot(
            on=data_loaded_columns[self.cleaning_log_question_column].data_column_name,
            index=clean_log_id_columns.data_column_name,
            values=[
                data_loaded_columns[
                    self.cleaning_log_new_value_column
                ].data_column_name,
                "is_update",
            ],
        ).rename(str.lower)
        # rename for later
        # the question prefix comes from the column name in the pivot operation
        unique_modified_rows_df = unique_modified_rows_df.rename(
            {
                f"{data_loaded_columns[self.cleaning_log_new_value_column].data_column_name}_{q}": f"{q}_val"
                for q in questions
            }
        ).rename({f"is_update_{q}": f"{q}_has_update" for q in questions})

        # filter the clean_data sheet to only have records that are in the cleaning log
        # and only select the questions that were present in the cleaning log
        # fill empty values to '' to make comparison easier later
        clean_data_filtered_df = (
            data_loaded_sheets[self.clean_data_sheet]
            .data.select([clean_data_id_columns.data_column_name] + questions)
            .filter(
                pl.col(clean_data_id_columns.data_column_name).is_in(
                    unique_modified_rows_df[
                        clean_log_id_columns.data_column_name
                    ].implode()
                )
            )
        )
        # .fill_null('')
        # join dataframes so columns can be matched below
        joined_df = unique_modified_rows_df.join(
            other=clean_data_filtered_df,
            left_on=clean_log_id_columns.data_column_name,
            right_on=clean_data_id_columns.data_column_name,
            how="left",
        )

        # build expressions to check for differences in the two dataframes
        difference_expressions = []
        for question in questions:
            col_has_update = f"{question}_has_update"
            # Check if the new value exists AND is different from the old value

            difference_expression = (
                create_column_difference_expression(
                    question,
                    f"{question}_val",
                    joined_df.schema[question],
                    joined_df.schema[f"{question}_val"],
                )
            ).alias(f"is_{question}_changed")

            difference_expression = (
                pl.when(pl.col(col_has_update).is_not_null())
                .then(difference_expression)
                .otherwise(pl.col(col_has_update).is_not_null())
            )

            difference_expressions.append(difference_expression)

        # Add the difference flags to the dataframe
        comparison_df = joined_df.with_columns(difference_expressions)
        # check for changes
        has_any_change = pl.any_horizontal(
            [pl.col(f"is_{question}_changed") for question in questions]
        )
        changes_only = comparison_df.filter(has_any_change)

        # record the changes
        # The unpivot process transforms the data from a wide format into a long format.
        #  By running this separately on the new values, old values, and change flags, we create three aligned vertical
        # lists that can be joined together using the uuid and question name. This allows us to filter for changes and compare
        # old vs. new values in a single operation.
        if not changes_only.is_empty():
            # unpivot new values
            new_values_df = changes_only.unpivot(
                index=[clean_log_id_columns.data_column_name]
                + [f"{q}_val" for q in questions],
                on=questions,
                variable_name="question",
                value_name=f"{self.cleaning_log_sheet}_value",
            )

            #    unpivot original values
            # need to rename so question names match
            original_values_df = (
                changes_only.select(
                    [clean_log_id_columns.data_column_name]
                    + [f"{q}_val" for q in questions]
                )
                .rename({f"{q}_val": q for q in questions})
                .unpivot(
                    index=[clean_log_id_columns.data_column_name],
                    on=questions,
                    variable_name="question",
                    value_name=f"{self.clean_data_sheet}_value",
                )
            )

            # unpivot flags. Extract question name from flag column name
            flags_long_df = changes_only.unpivot(
                index=[clean_log_id_columns.data_column_name],
                on=[f"is_{q}_changed" for q in questions],
                variable_name="flag_col_name",
                value_name="is_changed",
            ).with_columns(
                pl.col("flag_col_name")
                .str.replace("^is_", "", literal=False)
                .str.replace("_changed$", "", literal=False)
                .alias("question")
            )

            # join all together.  Filter the changed rows
            merged_df = (
                new_values_df.join(
                    original_values_df,
                    on=[clean_log_id_columns.data_column_name, "question"],
                    how="inner",
                )
                .join(
                    flags_long_df,
                    on=[clean_log_id_columns.data_column_name, "question"],
                    how="inner",
                )
                .filter(pl.col("is_changed"))
            )

            # select the columns because they are all present in the merged DF
            difference_df = merged_df.select(
                [
                    pl.col(clean_log_id_columns.data_column_name).alias(
                        clean_log_id_columns.data_column_name
                    ),
                    pl.col("question"),
                    pl.col(f"{self.cleaning_log_sheet}_value"),
                    pl.col(f"{self.clean_data_sheet}_value"),
                ]
            )

            # if there are differences found log them
            if difference_df.height > 0:
                df_to_csv(data=difference_df, filename=validation_results_filename)
                results.append(
                    ValidationResult(
                        rule=self.name,
                        message=f"There were {difference_df.height} differences found in the {self.cleaning_log_sheet} sheet that were not reflected in the {self.clean_data_sheet} sheet. Check the {validation_results_filename} file.",
                        severity=SeverityLevel.ERROR,
                        sheet_name=self.cleaning_log_sheet,
                        details=difference_df.to_dict(),
                    )
                )

        return results
