from pydub import AudioSegment
from pydub.silence import detect_silence


def get_audio_duration(file_path: str) -> float:
    """Возвращает длительность аудиофайла в секундах."""
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0  # pydub возвращает миллисекунды


def detect_silence_ranges(
    file_path: str,
    min_silence_len: int = 1000,
    silence_thresh: int = -40,
) -> list[tuple[float, float]]:
    """
    Обнаруживает диапазоны тишины в аудиофайле.

    Args:
        file_path: Путь к аудиофайлу.
        min_silence_len: Минимальная длина тишины в миллисекундах.
        silence_thresh: Порог громкости для определения тишины в dBFS.

    Returns:
        Список кортежей (start, end) в секундах.

    """
    audio = AudioSegment.from_file(file_path)
    silence_ranges_ms = detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
    )
    # Конвертируем миллисекунды в секунды
    return [(start / 1000.0, end / 1000.0) for start, end in silence_ranges_ms]


def generate_transcription(
    file_path: str,
    duration: float,
    max_length_sec: int = 20,
) -> str:
    """Генерирует 'псевдотранскрипцию'."""
    if duration <= max_length_sec:
        return "Detected speech fragment: Full recording analyzed."
    return f"Detected speech fragment: First {max_length_sec} seconds analyzed."
