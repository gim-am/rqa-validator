from pathlib import Path

import polars as pl
from config import settings

def df_to_csv(data: pl.DataFrame, 
              filename:str, 
              directory:Path = settings.VALIDATION_LOG_DIRECTORY):
    
    directory.mkdir(parents=True, exist_ok=True)
    data.write_csv(directory / filename)

