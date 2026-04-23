import re
from typing import  List
import polars as pl

from ..loaders.base import ColumnMap
from ..common.file_export import df_to_csv

from ..validators.base import ValidationResult, BaseValidator
from ..models.base_dataset import BaseDatasetSchema
from ..loaders.excel_loader import ExcelLoaderData
from . config import get_pii_columns
from ..common.list_matching import match_list_to_list
from config import settings


class MandatoryColumns(BaseValidator):

    @property
    def name(self) -> str:
        return 'MandatoryColumns'

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected mandatory columns are missing
        across relevant sheets. 

        Also checks if unique columns are missing.

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []
        for sheet in self.schema.schema_loaded_sheets:

            if not sheet.mandatory_columns:
                continue
            
            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)
            if loaded_sheet_info is not None:                
                
                for column in sheet.mandatory_columns:
                    if not loaded_sheet_info.get_column_map(column.standard_name):
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'A column for {column.standard_name} was expexted in the {loaded_sheet_info.data_sheet_name} sheet but was not found.'
                            ,severity = 'error'
                            ,sheet_name = loaded_sheet_info.data_sheet_name
                            ))  
                
                
            else:
                results.append(ValidationResult(
                                rule = self.name,
                                message = f'No sheet was loaded for {sheet.standard_name}.'
                                ,severity = 'error'
                                ,sheet_name = sheet.standard_name
                                )) 


        return results
    
class UniqueColumn(BaseValidator):

    @property
    def name(self) -> str:
        return 'UniqueColumn'

    def __init__(self, schema: BaseDatasetSchema):
        self.schema = schema

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks to see if any expected unique columns contain any
        non unique values across relevant sheets. 

        Saves duplicates to a csv

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: List of validation errors.
        """
        results: List[ValidationResult] = []   
        output_filename = 'duplicate_uuids'

        duplicated_ids_df: pl.DataFrame = pl.DataFrame([
                pl.Series("uuid",[], dtype=pl.String),
                pl.Series("sheet",[], dtype=pl.String)
            ])
            
        for sheet in self.schema.schema_loaded_sheets:

            unique_columns = sheet.get_unique_columns() 
            if not unique_columns:
                continue

            loaded_sheet_info = data.get_loaded_sheet(sheet.standard_name)

            if loaded_sheet_info:
                for column in unique_columns:
                    mapped_column = loaded_sheet_info.get_column_map(column.standard_name)
                    if mapped_column is not None:
                        unique_duplicated_rows_df = loaded_sheet_info.data.filter(loaded_sheet_info.data.select(mapped_column.data_column_name).is_duplicated())\
                                                                            .select(mapped_column.data_column_name)   \
                                                                            .rename({mapped_column.data_column_name: 'uuid'})
                        unique_duplicated_row_count = unique_duplicated_rows_df.n_unique()
                        if unique_duplicated_row_count > 0:
                            # store for output
                            unique_duplicated_rows_df = unique_duplicated_rows_df.unique().with_columns(pl.lit(loaded_sheet_info.data_sheet_name).alias('sheet') ) 
                            duplicated_ids_df = pl.concat([duplicated_ids_df, unique_duplicated_rows_df])
                            results.append(ValidationResult(
                                rule = self.name,
                                message = f'For column {mapped_column.data_column_name} in sheet {loaded_sheet_info.data_sheet_name} {unique_duplicated_row_count} non unique values were found. This column should contain unique values. Check {output_filename} file for details.'
                                ,severity = 'error'
                                ,sheet_name = loaded_sheet_info.schema_sheet_name
                                , details=unique_duplicated_rows_df.to_dict()
                                ))                            

        if duplicated_ids_df.height > 0:
            df_to_csv(duplicated_ids_df, output_filename)
                        
        return results



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
                                ,severity = 'warning'
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item
                                ))
            if fuzzy_matched_values:
                for item in fuzzy_matched_values:
                    results.append(ValidationResult(
                                rule = self.name + ' fuzzy match comparison',
                                message = f'The sheet {sheet.data_sheet_name} has a possible pii column. Check to the details to see if it should be removed.'
                                ,severity = 'warning'
                                ,sheet_name = sheet.data_sheet_name
                                ,column_name = item.standard_name
                                , details=item.matches
                                ))
            # scan column data
            id_column = sheet.get_column_map(id_column_standard_name)

            if id_column is None:
                id_column = ColumnMap(data_column_name='row_index',
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
                            ,severity = 'error'
                            ,sheet_name= sheet.data_sheet_name
                            ,details=final_df.to_dict()
                        ))  

                
        return results
    
class ColumnNameCheck(BaseValidator):
    """Check column names are variables instead of labels. 

    """
    @property
    def name(self) -> str:
        return 'ColumnNameCheck'

    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Check column names are variables instead of labels.

        This is done through regex matching that checks if there
        are any characters other than:
        - A-Z
        - a-z
        - 0-9
        - . or _

        Args:
            data (ExcelLoaderData): data to be validated

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: List[ValidationResult] = [] 
        pattern = re.compile(r'[^a-zA-Z_.\d:]')

        for sheet in data.loaded_sheets:
            matches = list(filter(pattern.search, sheet.data_columns))
            if matches:

                results.append(ValidationResult(
                    rule = self.name ,
                    message = f'The sheet {sheet.data_sheet_name} has column names that appear to be labels instead of variables. Check the output for details.'
                    ,severity = 'error'
                    ,sheet_name = sheet.data_sheet_name
                    , details= {sheet.data_sheet_name: matches}
                    ))

        return results