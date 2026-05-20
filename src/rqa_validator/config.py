from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils.logging import JIVELogger


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

    # for some validation rules and dynamic model creation
    IGNORE_COLUMNS_FOR_VALIDATION: list[str] = [
        "enum_id",
        "_index",
        "index",
        "_parent_index",
        "parent_index",
        "start",
        "end",
        "audit_url",
        "_id",
        "instance_name",
        "row_index",
    ]
    COMMON_ID_COLUMN_NAMES: list[str] = ["uuid", "x_uuid", "person_id"]

    # for dynamic model creation
    CLEAN_DATA_SHEET_SEARCH_TERMS: list[str] = ["clean", "clog_logbook"]
    CLEANING_LOG_SHEET_SEARCH_TERMS: list[str] = ["log"]
    RAW_DATA_SHEET_SEARCH_TERMS: list[str] = ["raw"]

    # for the NaNCheck validator
    NANCHECK_NUMERIC_VALUES: list = [-999, -99, 99, 999, -88, -888, 88, 888]
    NANCHECK_STRING_VALUES: list = [
        "-999",
        "-99",
        "99",
        "999",
        "-88",
        "-888",
        "88",
        "888",
    ]

    VALIDATION_LOG_DIRECTORY: Path = Path("../validation_logs")

    logger: JIVELogger = JIVELogger()


settings = Settings()
