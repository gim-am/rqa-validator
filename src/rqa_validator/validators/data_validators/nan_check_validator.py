from config import settings
from ...common.list_matching import filter_list
from ...validators.helpers import get_data_loaded_sheets, get_data_sheet_ids
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, ValidationResult, SeverityLevel


import polars as pl


from typing import List


class NaNCheck(BaseValidator):
    """Checks columns for invalid numeric values like NaN and -999.
    Invalid values are stored in the config file.

    """
    def __init__(self,
                 schema: BaseDatasetSchema,
                 check_sheets: List[str] = ['clean_data']) -> None:
        """
        Args:
            schema (BaseDatasetSchema): schema for the dataset
            sheets (List[str], optional): list of sheets to be checked. Defaults to ['clean_data'].
        """
        self.check_sheets = check_sheets
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
        
        result, data_loaded_sheets = get_data_loaded_sheets(data=data, 
                                                       sheet_names=self.check_sheets,
                                                        rule=self.name)

        if result:
            results.extend(result)
            return results
        
        result, sheet_ids = get_data_sheet_ids(self.schema, data_loaded_sheets, self.name)
        if result:
            results.extend(result)
            return results


        for sheet in self.check_sheets:     

            nan_value_expressions = []
            filtered_columns = filter_list(data_loaded_sheets[sheet].data.columns,settings.IGNORE_COLUMNS_FOR_VALIDATION )
            filtered_df = data_loaded_sheets[sheet].data.select(filtered_columns)

            # build expression to find possible invalid values or NaNs
            for column in filtered_columns:
                expression = pl.any_horizontal(
                    (
                        (pl.col(column).is_nan() | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES))) if filtered_df.schema[column].is_float() else False
                        | (pl.col(column).is_in( settings.NANCHECK_NUMERIC_VALUES) ) if filtered_df.schema[column].is_integer() else False
                        | (pl.col(column).is_in( settings.NANCHECK_STRING_VALUES) ) if filtered_df.schema[column] == pl.String else pl.lit(False)

                    ).alias(f"is_{column}_nan_value")

                )
                nan_value_expressions.append(expression)

            # get a df that has nan/invalid data in a row
            nan_df = filtered_df.with_columns(nan_value_expressions)
            has_nan = pl.any_horizontal([pl.col(f"is_{column}_nan_value") for column in filtered_columns])
            nan_only_df = nan_df.filter(has_nan)

            output_rows = []

            # create df of only invalid data
            if not nan_only_df.is_empty():
                for row in nan_only_df.iter_rows(named=True):
                    uuid = row[sheet_ids[sheet][0].data_column_name]
                    for column in filtered_columns:
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
                                                        pl.DataFrame(output_rows, 
                                                                     infer_schema_length=None)])


        if output_difference_df.height > 0:
            # df_to_csv(data=difference_df, filename=validation_results_filename)
            results.append(ValidationResult(
                rule = self.name,
                message = f'There were {output_difference_df.height} possible invalid values found. Check the output results for details.'
                ,severity = SeverityLevel.ERROR
                ,details=output_difference_df.to_dict()
            ))

        return results