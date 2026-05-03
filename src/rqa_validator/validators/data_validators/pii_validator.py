from config import settings
from ...common.list_matching import match_list_to_list
from ...loaders.base import DataColumnMap
from ...loaders.excel_loader import ExcelLoaderData
from ...validators.base import BaseValidator, ValidationResult, SeverityLevel
from ...validators.config import get_pii_columns


import polars as pl


from typing import List


class PiiColumns(BaseValidator):
    """Checks all the sheets for possible PII Data"""

    @property
    def name(self) -> str:
        return 'PiiColumns'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """This performs two sets of checks

        First: checks to see if any pii columns are present across relevant sheets. 
            Possible pii columns are currently stored in models/config.
            Fuzzy matching is also optionally performed.

        Second: performs regex matching on sheets for possible pii data.
            Currently matching is fairly simple and limited to:
            - emails
            - possible phone numbers: must start with a 0 or +
                and not be a decimal. This is a limited implementaion.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        pii_columns = get_pii_columns()

        id_column_standard_name = 'uuid'

        patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",

            # This is limited. Currently looking for numbers starting
            # with a + or 0. Does not match decimals
            "phone": r'^(\+|0)[\d\s\-\(\)\+]+$'
            }

        expressions = [
            pl.col("value").cast(pl.Utf8).str
                                .extract(pattern, 0)
                                .alias(f"match_{type}")
            for type, pattern in patterns.items()
        ]

        for sheet in data.loaded_sheets:
            # scan column names
            literal_matches, fuzzy_matched_values = match_list_to_list(sheet.data.columns, pii_columns, settings.FUZZY_MATCH_COLUMNS)

            if literal_matches:
                for item in literal_matches:
                    results.append(ValidationResult(
                                rule = self.name + ' literal comparison',
                                message = f'The sheet {sheet.data_sheet_name} has a possible pii column. Check to see if it should be removed: {item}.'
                                ,severity = SeverityLevel.WARNING
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item
                                ))
            if fuzzy_matched_values:
                for item in fuzzy_matched_values:
                    results.append(ValidationResult(
                                rule = self.name + ' fuzzy match comparison',
                                message = f'The sheet {sheet.data_sheet_name} has a possible pii column. Check to the details to see if it should be removed.'
                                ,severity = SeverityLevel.WARNING
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item.standard_name
                                , details=item.matches
                                ))
            # scan column data
            id_column = sheet.get_column_map(id_column_standard_name)

            if id_column is None:
                id_column = DataColumnMap(data_column_name='row_index',
                                      schema_column_name='row_index')
                melted_df = sheet.data.with_row_index(id_column.data_column_name) \
                                        .unpivot(index=id_column.data_column_name,
                                                variable_name="column_name",
                                                value_name="value")
            else:
            # unpivot to make showing the results easier
                melted_df = sheet.data.unpivot(index=id_column.data_column_name,
                                                variable_name="column_name",
                                                value_name="value")

            # add expression columns
            melted_df = melted_df.with_columns(expressions)
            # build match conditions
            match_conditions = [pl.col(name=f"match_{t}").is_not_null() for t in patterns.keys()]

            # apply conditions and filter the data
            any_match_condition = pl.any_horizontal(match_conditions)
            filtered_df = melted_df.filter(any_match_condition)

            match_cols = [f"match_{t}" for t in patterns.keys()]

            # format results for output
            final_df = filtered_df.unpivot(
                index=[id_column.data_column_name, "column_name"],
                on=match_cols,
                variable_name="pii_type_raw",
                value_name="matched_value"
            )
            # unpivot will add extra rows so remove those that havent actually matched
            final_df = final_df.filter(pl.col("matched_value").is_not_null())

            final_df = final_df.with_columns(pl.col("pii_type_raw").str
                                             .replace("match_", "")
                                             .alias("pii_type")
                                            ).select([
                                                id_column.data_column_name,
                                                "column_name",
                                                "pii_type",
                                                "matched_value"
                                            ])

            if final_df.height > 0:
                results.append(ValidationResult(
                            rule = self.name,
                            message = f'The sheet {sheet.data_sheet_name} contains possible pii data. Check the output for details.'
                            ,severity = SeverityLevel.ERROR
                            ,sheet_name= sheet.data_sheet_name
                            ,details=final_df.to_dict()
                        ))


        return results