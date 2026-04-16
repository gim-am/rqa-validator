from datetime import datetime,timezone
from pathlib import Path

import polars as pl
from config import settings

def df_to_csv(data: pl.DataFrame, 
              filename:str, 
              directory:Path = settings.VALIDATION_LOG_DIRECTORY):
    """Saves dataframe to a csv. Adds a timestamp to the file

    Args:
        data (pl.DataFrame): data to be saved
        filename (str): name of the file. Does not need to include .csv extension.
        directory (Path, optional): directory to save the file. Defaults to settings.VALIDATION_LOG_DIRECTORY.
    """
    output = str((directory / filename).with_suffix('')) \
          + (datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S") \
              + '.csv'

    directory.mkdir(parents=True, exist_ok=True)
    data.write_csv(output)

