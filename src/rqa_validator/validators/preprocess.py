

from ..loaders.excel_loader import ExcelLoaderData
from ..models.schema import BaseDatasetSchema


def match_columns(schema: BaseDatasetSchema, data: ExcelLoaderData):
    # TODO: match schema columns to df columns if no literal match

    pass

# sheet matching done in excel loader
    # check for duplicate matched sheets - prevalidated schema so shouldnt happen
# match loaded columns to schema columns
# move to excel loader?
    # for sheet in schema.schema_loaded_sheets:
    #     sheet_loaded_info = data.get_loaded_sheet(sheet.standard_name)
    #     if sheet_loaded_info is not None:

    #         search_mandatory_columns = sheet.mandatory_columns
    #         search_unique_columns = sheet.unique_columns
    #         source_columns = sheet_loaded_info.columns

            



# match excel sheet to schema - done in loader
# match schema sheet mandatory columns to excel sheet columns
# match schema sheet unique column to excel cheet columns