from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from src.rqa_validator.utils.logging import JIVELogger

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    FUZZY_MATCH_SHEETS: bool = True
    FUZZY_MATCH_COLUMNS: bool = True
    MIN_FUZZY_MATCH_SCORE: int = 90
    FUZZY_MATCH_STRING_LENGTH_RATIO: float = 0.7

    # for the NaNCheck validator 
    NANCHECK_NUMERIC_VALUES: List =  [-999,-99,99, 999, -88, -888, 88, 888]
    NANCHECK_STRING_VALUES: List = ['-999','-99','99', '999', '-88', '-888', '88', '888'] 

    VALIDATION_LOG_DIRECTORY: Path = Path('../validation_logs')

    logger: JIVELogger = JIVELogger()

settings = Settings()

