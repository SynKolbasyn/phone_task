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


from pydub import AudioSegment
from pydub.silence import detect_silence


def process_audio(file_path: str) -> tuple[float, str, list[tuple[float, float]]]:
    audio = AudioSegment.from_file(file_path)

    duration = len(audio) / 1000.0

    transcription = " ".join(f"word-{i}" for i in range(round(duration)))

    silence_ranges_ms = detect_silence(
        audio,
        min_silence_len=1000,
        silence_thresh=-40,
    )
    silent_ranges_sec: list[tuple[float, float]] = [
        (start / 1000.0, end / 1000.0) for start, end in silence_ranges_ms
    ]

    return duration, transcription, silent_ranges_sec
