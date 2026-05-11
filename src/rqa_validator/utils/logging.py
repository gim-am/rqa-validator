import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class JIVELogger:
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("jive")
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Timed rotating file handler - rotates at midnight
        file_handler = TimedRotatingFileHandler(
            self.log_dir / "jive.log",
            when="midnight",  # Rotate at midnight
            interval=1,  # Every 1 day
            backupCount=30,  # Keep 30 days of old logs
            encoding="utf-8",
        )

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_error(self, message: str):
        self.logger.error(message)

    def log_exception(self, message: object):
        self.logger.exception(message)
