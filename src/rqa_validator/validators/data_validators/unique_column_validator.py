import polars as pl

from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, SeverityLevel, ValidationResult


class UniqueColumn(BaseValidator):
    @property
    def name(self) -> str:
        return "UniqueColumn"

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> list[ValidationResult]:
        """Checks to see if any expected unique columns contain any
        non unique values across relevant sheets.

        Saves duplicates to a csv

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: list[ValidationResult] = []
        # output_filename = "duplicate_uuids"

        duplicated_ids_df: pl.DataFrame = pl.DataFrame(
            [
                pl.Series("uuid", [], dtype=pl.String),
                pl.Series("sheet", [], dtype=pl.String),
            ]
        )

        for sheet in self.schema.schema_loaded_sheets:
            unique_columns = sheet.get_unique_columns()
            if not unique_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)

            if loaded_sheet_info:
                for column in unique_columns:
                    mapped_column = loaded_sheet_info.get_column_map(column.standard_name)
                    if mapped_column is not None:
                        unique_duplicated_rows_df = (
                            loaded_sheet_info.data.filter(
                                loaded_sheet_info.data.select(
                                    mapped_column.data_column_name
                                ).is_duplicated()
                            )
                            .select(mapped_column.data_column_name)
                            .rename({mapped_column.data_column_name: "uuid"})
                        )
                        unique_duplicated_row_count = unique_duplicated_rows_df.n_unique()
                        if unique_duplicated_row_count > 0:
                            # store for output
                            unique_duplicated_rows_df = (
                                unique_duplicated_rows_df.unique().with_columns(
                                    pl.lit(loaded_sheet_info.data_sheet_name).alias("sheet")
                                )
                            )
                            duplicated_ids_df = pl.concat(
                                [duplicated_ids_df, unique_duplicated_rows_df]
                            )
                            results.append(
                                ValidationResult(
                                    rule=self.name,
                                    message=self._(
                                        "unique_column_validator.non_unique",
                                        column=mapped_column.data_column_name,
                                        sheet=loaded_sheet_info.data_sheet_name,
                                        count=unique_duplicated_row_count,
                                    ),
                                    severity=SeverityLevel.ERROR,
                                    sheet_name=loaded_sheet_info.schema_sheet_name,
                                    details=unique_duplicated_rows_df.to_dict(as_series=False),
                                )
                            )

        return results
