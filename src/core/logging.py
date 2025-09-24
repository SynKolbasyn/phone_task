from logging import INFO, FileHandler, StreamHandler, basicConfig
from sys import stdout

from config import Settings


def setup_logging() -> None:
    logs_dir = Settings().base_dir / "logs/" / "access.log"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logging_format = (
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    )
    basicConfig(
        format=logging_format,
        datefmt="%d.%m.%Y %H:%M:%S",
        level=INFO,
        handlers=[
            StreamHandler(stdout),
            FileHandler(logs_dir / "logs.log", encoding="utf-8"),
        ],
        encoding="utf-8",
    )
