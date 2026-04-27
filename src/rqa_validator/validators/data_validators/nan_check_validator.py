from config import settings
from rqa_validator.common.schema_matching import get_matching_unique_columns
from rqa_validator.loaders.excel_loader import ExcelLoaderData
from rqa_validator.models.base_dataset import BaseDatasetSchema
from rqa_validator.validators.base import BaseValidator, ValidationResult


import polars as pl


from typing import List


class NaNCheck(BaseValidator):
    """Checks columns for invalid numeric values like NaN and -999.
    Invalid values are stored in the config file.

    """
    def __init__(self,
                 schema: BaseDatasetSchema,
                 sheets: List[str] = ['clean_data']) -> None:
        """
        Args:
            schema (BaseDatasetSchema): schema for the dataset
            sheets (List[str], optional): list of sheets to be checked. Defaults to ['clean_data'].
        """
        self.sheets = sheets
        self.schema = schema

    @property
    def name(self) -> str:
        return 'NaNCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks columns for invalid numeric values like NaN and -999.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []

        output_difference_df =  pl.DataFrame([
                pl.Series("uuid",[], dtype=pl.String),
                pl.Series("sheet",[], dtype=pl.String),
                pl.Series("column",[], dtype=pl.String),
                pl.Series("value",[], dtype=pl.String)
            ])

        for sheet in self.sheets:
            loaded_sheet = data.get_loaded_sheet(sheet)

            if loaded_sheet is None:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A sheet for {sheet} is expected.'
                    ,severity = 'error'
                    ,sheet_name=sheet
                ))
                continue

            # get id column for the output dataframe
            id_column = get_matching_unique_columns(schema=self.schema,
                                              loaded_data=loaded_sheet,
                                              sheet_name=sheet)

            if len(id_column) != 1:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A single unique column for schema sheet {sheet} and matching excel sheet {loaded_sheet.data_sheet_name} was expected.'
                    ,severity = 'error'
                    ,sheet_name=sheet
                ))
                continue

            id_column = id_column[0]

            nan_value_expressions = []

            # build expression to find possible invalid values or NaNs
            for column in loaded_sheet.data.columns:

                expression = pl.any_horizontal(
                    (
                        (pl.col(column).is_nan() | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES))) if loaded_sheet.data.schema[column].is_float() else False
                        | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES) ) if loaded_sheet.data.schema[column].is_integer() else False
                        | (pl.col(column).is_in( settings.NANCHECK_STRING_VALUES) ) if loaded_sheet.data.schema[column] == pl.String else pl.lit(False)

                    ).alias(f"is_{column}_nan_value")

                )
                nan_value_expressions.append(expression)

            # get a df that has nan/invalid data in a row
            nan_df = loaded_sheet.data.with_columns(nan_value_expressions)
            has_nan = pl.any_horizontal([pl.col(f"is_{column}_nan_value") for column in loaded_sheet.data.columns])
            nan_only_df = nan_df.filter(has_nan)

            output_rows = []

            # create df of only invalid data
            if not nan_only_df.is_empty():
                for row in nan_only_df.iter_rows(named=True):
                    uuid = row[id_column.data_column_name]
                    for column in loaded_sheet.data.columns:
                        is_changed = row[f"is_{column}_nan_value"]

                        if is_changed:
                            value = row[column]
                            # new_val = row[new_col]
                            output_rows.append({
                                "uuid": uuid,
                                "sheet": sheet,
                                "column": column,
                                "value": str(value),
                            })
                output_difference_df = pl.concat([output_difference_df,
                                                        pl.DataFrame(output_rows, infer_schema_length=None)])


        if output_difference_df.height > 0:
            # df_to_csv(data=difference_df, filename=validation_results_filename)
            results.append(ValidationResult(
                rule = self.name,
                message = f'There were {output_difference_df.height} possible invalid values found. Check the output results for details.'
                ,severity = 'error'
                ,details=output_difference_df.to_dict()
            ))

        return results