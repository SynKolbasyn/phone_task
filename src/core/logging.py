from logging import INFO, FileHandler, StreamHandler, basicConfig
from sys import stdout

from config import Settings


def setup_logging() -> None:
    """Set up logging configuration."""
    logs_dir = Settings().base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "access.log"
    
    logging_format = (
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    )
    basicConfig(
        format=logging_format,
        datefmt="%d.%m.%Y %H:%M:%S",
        level=INFO,
        handlers=[
            StreamHandler(stdout),
            FileHandler(log_file, encoding="utf-8"),
        ],
        encoding="utf-8",
    )
