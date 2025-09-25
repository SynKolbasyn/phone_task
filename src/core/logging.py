"""
Phone Call Service.

Copyright (C) 2025  Andrew Kozmin <syn.kolbasyn.06@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from logging import INFO, FileHandler, StreamHandler, basicConfig
from sys import stdout

from config import Settings


def setup_logging() -> None:
    logs_dir = Settings().base_dir / "logs/" / "fastapi"
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
            FileHandler(logs_dir / "access.log", encoding="utf-8"),
        ],
        encoding="utf-8",
    )
