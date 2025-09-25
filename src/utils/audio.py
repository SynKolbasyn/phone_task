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
