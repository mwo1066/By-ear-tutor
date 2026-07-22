"""Microphone capture (push-to-talk) + faster-whisper transcription.

Push-to-talk for now (press Enter to start, Enter again to stop) --
simpler than real VAD/silence-detection, good enough to prove the pipeline.
"""
import queue
import sys
import threading

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print("  (chargement du modele Whisper, une seule fois...)")
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model


def record_until_enter() -> np.ndarray:
    """Records from the default mic until the user presses Enter again."""
    frames: list[np.ndarray] = []
    stop_event = threading.Event()

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback
    )
    print("  [enregistrement en cours -- appuie sur Entree pour arreter]")
    with stream:
        input()  # blocks until Enter, while callback keeps appending frames
    if not frames:
        return np.array([], dtype=np.int16)
    return np.concatenate(frames, axis=0).flatten()


def transcribe(audio: np.ndarray) -> tuple[str, str]:
    """Returns (text, language_code)."""
    if audio.size == 0:
        return "", "en"
    audio_float = audio.astype(np.float32) / 32768.0
    model = _get_model()
    # vad_filter trims silence before/around speech -- without it, silence-
    # padded push-to-talk recordings can make Whisper hallucinate repeated
    # phrases (seen live: "I don't know why, I don't know why...").
    segments, info = model.transcribe(
        audio_float, beam_size=5, vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip(), info.language


def listen_and_transcribe() -> str:
    """Full push-to-talk turn: record, transcribe, return a [lang:xx]-tagged string."""
    audio = record_until_enter()
    text, lang = transcribe(audio)
    if not text:
        return ""
    return f"[lang:{lang}] {text}"
