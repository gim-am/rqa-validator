from typing import List
import polars as pl

from ...common.schema_matching import get_matching_unique_columns
from ...loaders.excel_loader import ExcelLoaderData
from ...models.base_dataset import BaseDatasetSchema
from ...validators.base import BaseValidator, ValidationResult




class DataTypeCheck(BaseValidator):
    """Checks that columns and column values are the correct datatype
        based on the kobo survey.
    """
    def __init__(self,
                 schema: BaseDatasetSchema,
                 survey_sheet: str = 'kobo_survey',
                 survey_type_column: str = 'type',
                 survey_name_column: str = 'name',
                 check_sheets: List = ['clean_data']) -> None:
        """

        Args:
            schema (BaseDatasetSchema): dataset schema
            survey_sheet (str, optional): name of the kobo survey sheet in excel. Defaults to 'kobo_survey'.
            survey_type_column (str, optional): name of the type column in the kobo survey sheet. Defaults to 'type'.
            survey_name_column (str, optional): name of the name column in the kobo survey sheet. Defaults to 'name'.
            check_sheets (List, optional): schema sheet names to check. Defaults to ['clean_data'].
        """
        self.survey_sheet = survey_sheet
        self.check_sheets = check_sheets
        self.survey_type_column = survey_type_column
        self.survey_name_column = survey_name_column
        self.schema = schema
        self.process_value_map_name_numeric = 'data_type_numeric_check'
        self.process_value_map_name_temporal = 'data_type_temporal_check'

    @property
    def name(self) -> str:
        return 'DataTypeCheck'
    
    def validate(self, data: ExcelLoaderData) -> List[ValidationResult]:
        """Checks that columns and column values are the correct datatype
        based on the kobo survey.

        Currently checking numeric and temporal columns.

        Expects process_values to be present for the kobo_survey schema sheet
        in the type column to store both the numeric and temporal datatype names
        found in the kobo_survey type column

        if a column is the correct data type then its safe to assume that
        all the values are the correct datatype

        if the column is the incorrect data type then the values are checked.

        Args:
            data (ExcelLoaderData): excel data to validate

        Returns:
            List[ValidationResult]: list of validation errors
        """
        results: List[ValidationResult] = []
        # pre-validation

        loaded_survey_sheet = data.get_loaded_sheet(self.survey_sheet)

        if loaded_survey_sheet is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'An excel sheet for {self.survey_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.survey_sheet
            ))
            return results
        
        type_column = loaded_survey_sheet.get_column_map(self.survey_type_column)
        if type_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.survey_type_column} in excel sheet {loaded_survey_sheet.data_sheet_name} is expected.'
                ,severity = 'error'
                ,sheet_name=loaded_survey_sheet.data_sheet_name
            ))
            return results
        
        name_column = loaded_survey_sheet.get_column_map(self.survey_name_column)
        if name_column is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {self.survey_name_column} in excel sheet {loaded_survey_sheet.data_sheet_name} is expected.'
                ,severity = 'error'
                ,sheet_name=loaded_survey_sheet.data_sheet_name
            ))
            return results
        
        schema_survey_sheet = self.schema.get_schema_loaded_sheet(self.survey_sheet)

        if schema_survey_sheet is None:
            results.append(ValidationResult(
                rule = self.name,
                message = f'A schema sheet for {self.survey_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.survey_sheet
            ))
            return results
        
        schema_type_column = schema_survey_sheet.get_column(type_column.schema_column_name)

        if schema_type_column is None:
            # should not actually happen as its already mapped above.
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {type_column.schema_column_name} in schema sheet {self.survey_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.survey_sheet
            ))
            return results
        
        schema_name_column = schema_survey_sheet.get_column(name_column.schema_column_name)

        if schema_name_column is None:
            # should not actually happen as its already mapped above.
            results.append(ValidationResult(
                rule = self.name,
                message = f'A column for {name_column.schema_column_name} in schema sheet {self.survey_sheet} is expected.'
                ,severity = 'error'
                ,sheet_name=self.survey_sheet
            ))
            return results
        
        type_values_numeric = schema_type_column.get_process_values(self.process_value_map_name_numeric)
        if type_values_numeric is None or len(type_values_numeric.values) == 0:
            results.append(ValidationResult(
            rule = self.name,
            message = f'process_values were expected for column {name_column.schema_column_name} for process {self.process_value_map_name_numeric}.'
            ,severity = 'error'
            , sheet_name= self.survey_sheet
            , column_name=name_column.schema_column_name
            ))
            return results
        
        type_values_temporal = schema_type_column.get_process_values(self.process_value_map_name_temporal)
        if type_values_temporal is None or len(type_values_temporal.values) == 0:
            results.append(ValidationResult(
            rule = self.name,
            message = f'process_values were expected for column {name_column.schema_column_name} for process {self.process_value_map_name_temporal}.'
            ,severity = 'error'
            , sheet_name= self.survey_sheet
            , column_name=name_column.schema_column_name
            ))
            return results
        
        # get the columns that need checking
        numeric_columns = loaded_survey_sheet.data.filter(pl.col(type_column.data_column_name)
                                                                .str
                                                                .to_lowercase()
                                                                .is_in(type_values_numeric.values)) \
                                                    .select([name_column.data_column_name])\
                                                    .to_series().str.to_lowercase().to_list()
        temporal_columns = loaded_survey_sheet.data.filter(pl.col(type_column.data_column_name)
                                                            .str
                                                            .to_lowercase()
                                                            .is_in(type_values_temporal.values)) \
                                                    .select([name_column.data_column_name]) \
                                                    .to_series().str.to_lowercase().to_list()
        
        
        for sheet in self.check_sheets:
            # validate the sheet
            loaded_check_sheet = data.get_loaded_sheet(sheet)

            if loaded_check_sheet is None:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'An excel sheet for {sheet} is expected.'
                    ,severity = 'error'
                    ,sheet_name=self.survey_sheet
                ))
                continue

            check_sheet_id_column = get_matching_unique_columns(schema=self.schema,
                                        loaded_data=loaded_check_sheet,
                                        sheet_name=sheet)

            if len(check_sheet_id_column) != 1:
                results.append(ValidationResult(
                    rule = self.name,
                    message = f'A single unique column for schema sheet {sheet} and matching excel sheet {loaded_check_sheet.data_sheet_name} was expected.'
                    ,severity = 'error'
                    ,sheet_name=sheet
                ))
                continue

            check_sheet_id_column = check_sheet_id_column[0]            

            # numeric check
            if numeric_columns:
                # check the data types of the data frame columns
                incorrect_data_type_columns = [item for item in numeric_columns if not loaded_check_sheet.data.schema[item].is_numeric()]
                
                if incorrect_data_type_columns:
                    # if there are dataframe columns with the incorrect data type
                    # then check the column values

                    # pivot the table to make the process easier
                    check_df = loaded_check_sheet.data.select([check_sheet_id_column.data_column_name] + 
                                                                incorrect_data_type_columns)\
                                                        .unpivot(index=check_sheet_id_column.data_column_name,
                                                                    variable_name='question',
                                                                    value_name='value')
                    # find invalid values
                    # if the value cant be converted it will return null.
                    # this is used as a filter on the dataframe
                    incorrect_values_df = check_df.filter(pl.col('value').is_not_null()) \
                                                    .filter(pl.col('value')
                                                            .cast(pl.Float64, strict=False)
                                                            .is_null())
                                       
                    if incorrect_values_df.height > 0:
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'Non-numeric values were found in {sheet} when numeric values were expected. Check the output for details.'
                            ,severity = 'error'
                            ,sheet_name=sheet
                            , details=incorrect_values_df.to_dict()
                        ))

            # temporal check
            if temporal_columns:
                # check the data types of the data frame columns
                incorrect_data_type_columns = [item for item in temporal_columns if not loaded_check_sheet.data.schema[item].is_temporal()]

                if incorrect_data_type_columns:
                     # if there are dataframe columns with the incorrect data type
                    # then check the column values

                    # pivot the table to make the process easier
                    check_df = loaded_check_sheet.data.select([check_sheet_id_column.data_column_name] + 
                                                                incorrect_data_type_columns)\
                                                        .unpivot(index=check_sheet_id_column.data_column_name,
                                                                    variable_name='question',
                                                                    value_name='value')
                    # find invalid values
                    # if the value cant be converted it will return null.
                    # this is used as a filter on the dataframe
                    incorrect_values_df = check_df.filter(pl.col('value').is_not_null()) \
                                                    .filter(pl.col('value')
                                                            .str.to_datetime(strict=False)
                                                    # .cast(pl.Datetime, strict=False)
                                                            .is_null())
                    
                    if incorrect_values_df.height > 0:
                        results.append(ValidationResult(
                            rule = self.name,
                            message = f'Non-temporal values were found in {sheet} when temporal values were expected. Check the output for details.'
                            ,severity = 'error'
                            ,sheet_name=sheet
                            , details=incorrect_values_df.to_dict()
                        ))

        return results