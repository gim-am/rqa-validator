from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    FUZZY_MATCH_SHEETS: bool = True
    FUZZY_MATCH_COLUMNS: bool = True
    MIN_FUZZY_MATCH_SCORE: int = 95
    # FUZZY_MATCH_SCORER = fuzz.WRatio()

    # for the NaNCheck validator 
    NANCHECK_NUMERIC_VALUES: List =  [999, -999]
    NANCHECK_STRING_VALUES: List = ["999", "-999"] 

    VALIDATION_LOG_DIRECTORY: Path = Path('../validation_logs')

settings = Settings()

