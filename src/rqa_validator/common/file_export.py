from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from config import settings


def df_to_csv(
    data: pl.DataFrame,
    filename: str,
    directory: Path = settings.VALIDATION_LOG_DIRECTORY,
    add_timestamp: bool = False,
):
    """Saves dataframe to a csv.

    Args:
        data (pl.DataFrame): data to be saved
        filename (str): name of the file. Does not need to include .csv extension.
        directory (Path, optional): directory to save the file.
            Defaults to settings.VALIDATION_LOG_DIRECTORY.
        add_timestamp (bool, optional): add a timestamp to the filename
    """
    timestamp = ""
    if add_timestamp:
        timestamp = (datetime.now(UTC)).strftime("%Y%m%d-%H%M%S")

    output = str((directory / filename).with_suffix("")) + timestamp + ".csv"

    directory.mkdir(parents=True, exist_ok=True)
    data.write_csv(output)
