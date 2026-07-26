"""Microphone capture (automatic silence detection, like memai's client)
+ faster-whisper transcription.

Uses webrtcvad frame-by-frame, same approach and aggressiveness (2) as
memai's own client: waits for speech to start, keeps recording through it,
and stops automatically after a stretch of trailing silence -- no key to
press to end your turn.
"""
import time

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480 samples/frame at 16kHz/30ms

VAD_AGGRESSIVENESS = 2
TRAILING_SILENCE_MS = 1200        # stop after this much silence once speech has started
MAX_WAIT_FOR_SPEECH_S = 10        # give up if nobody starts talking
MAX_RECORDING_S = 30              # hard safety cap

_model: WhisperModel | None = None
_vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print("  (chargement du modele Whisper, une seule fois...)")
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model


def preload_model() -> None:
    """Loads the Whisper model up front so the cost doesn't land on the
    first real listen -- found live: the first listen_and_transcribe() call
    ate both the VAD wait AND several seconds of model loading, sometimes
    eating into the speech-detection window itself and causing a missed turn."""
    _get_model()


def record_until_silence() -> np.ndarray:
    """Records from the default mic, starting once speech is detected and
    stopping automatically after TRAILING_SILENCE_MS of silence."""
    frames: list[np.ndarray] = []
    speech_started = False
    frames_needed_silence = TRAILING_SILENCE_MS // FRAME_MS
    consecutive_silence_frames = 0
    start_time = time.monotonic()
    done = False

    def callback(indata, frame_count, time_info, status):
        nonlocal speech_started, consecutive_silence_frames, done
        if done:
            return
        chunk = indata.copy()
        frames.append(chunk)
        is_speech = _vad.is_speech(chunk.tobytes(), SAMPLE_RATE)
        if is_speech:
            speech_started = True
            consecutive_silence_frames = 0
        elif speech_started:
            consecutive_silence_frames += 1
            if consecutive_silence_frames >= frames_needed_silence:
                done = True

    print("  [ecoute en cours -- parle maintenant. NE RAPPUIE PAS sur Entree, ca s'arrete tout seul quand tu te tais]")
    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16",
        blocksize=FRAME_SAMPLES, callback=callback,
    ):
        while not done:
            time.sleep(0.05)
            elapsed = time.monotonic() - start_time
            if not speech_started and elapsed > MAX_WAIT_FOR_SPEECH_S:
                break
            if elapsed > MAX_RECORDING_S:
                break

    if not frames:
        return np.array([], dtype=np.int16)
    return np.concatenate(frames, axis=0).flatten()


def record_until_enter() -> np.ndarray:
    """Push-to-talk: press Enter to start, Enter again to stop. Faster to
    iterate with while testing -- no VAD trailing-silence wait, no risk of
    it cutting you off early or missing a quiet start."""
    frames: list[np.ndarray] = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback
    )
    print("  [enregistrement -- appuie sur Entree pour ARRETER]")
    with stream:
        input()
    if not frames:
        return np.array([], dtype=np.int16)
    return np.concatenate(frames, axis=0).flatten()


# Only languages that actually make sense here: the target language, and
# the learner's own. Whisper's full language auto-detect will happily guess
# Polish or Japanese from a few unclear syllables -- found live, attempts at
# "tôi" got tagged [lang:pl]/[lang:ja]. Anything outside this set almost
# certainly means "mangled pronunciation attempt", which the persona prompt
# already knows how to handle -- so it gets normalized to "vi" instead of
# passing through a meaningless exotic tag.
ALLOWED_LANGUAGES = {"vi", "en", "fr"}


def _run_transcribe(audio_float, language: str | None):
    segments, info = _get_model().transcribe(
        audio_float, beam_size=5, vad_filter=True, language=language,
        # vad_filter trims silence before/around speech -- without it, silence-
        # padded recordings can make Whisper hallucinate repeated phrases
        # (seen live: "I don't know why, I don't know why...").
        vad_parameters={"min_silence_duration_ms": 500},
    )
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip(), info.language


def transcribe(audio: np.ndarray) -> tuple[str, str]:
    """Returns (text, language_code), language_code always in ALLOWED_LANGUAGES."""
    if audio.size == 0:
        return "", "en"
    audio_float = audio.astype(np.float32) / 32768.0
    text, lang = _run_transcribe(audio_float, language=None)  # auto-detect first
    if lang not in ALLOWED_LANGUAGES:
        # Auto-detect landed on something nonsensical for this context (seen
        # live: literal Japanese/Korean script from a mangled pronunciation
        # attempt) -- clamping just the language TAG before left the actual
        # transcribed text in that foreign script, useless to the tutor.
        # Re-run forcing Vietnamese phonetics instead of trusting the guess.
        text, _ = _run_transcribe(audio_float, language="vi")
        lang = "vi"
    return text, lang


# Swap to record_until_silence for the real hands-free experience once
# testing settles down -- push-to-talk for now, deliberately, to iterate
# fast without the VAD's trailing-silence wait on every single turn.
USE_PUSH_TO_TALK = True


def listen_and_transcribe() -> str:
    """Full turn: listen (push-to-talk or hands-free per USE_PUSH_TO_TALK),
    transcribe, return a [lang:xx]-tagged string."""
    audio = record_until_enter() if USE_PUSH_TO_TALK else record_until_silence()
    text, lang = transcribe(audio)
    if not text:
        return ""
    return f"[lang:{lang}] {text}"
