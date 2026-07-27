"""Microphone capture (automatic silence detection, like memai's client)
+ faster-whisper transcription.

Uses webrtcvad frame-by-frame, same approach and aggressiveness (2) as
memai's own client: waits for speech to start, keeps recording through it,
and stops automatically after a stretch of trailing silence -- no key to
press to end your turn.
"""
import io
import json
import time
import urllib.error
import urllib.request
import uuid
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
import webrtcvad
from faster_whisper import WhisperModel

ENV_PATH = Path(__file__).parent / ".env"

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480 samples/frame at 16kHz/30ms

VAD_AGGRESSIVENESS = 3  # max strictness -- found live: background noise (fan,
# room echo) was misclassified as speech 10x in one turn, repeatedly resetting
# the trailing-silence countdown and dragging recordings out to 7-9s+ for a
# short utterance. aggressiveness=2 was too lenient for this mic/environment.
TRAILING_SILENCE_MS = 1200        # stop after this much silence once speech has started
MAX_WAIT_FOR_SPEECH_S = 10        # give up if nobody starts talking
MAX_RECORDING_S = 30              # hard safety cap

_model: WhisperModel | None = None
_vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print("  (chargement du modele Whisper, une seule fois...)")
        # cpu_threads=8: benchmarked live on this machine (12 logical cores) --
        # the default under-uses available cores; 8 threads gave a consistent
        # ~15-20% speedup over default, with 12 threads no better (overhead).
        _model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
    return _model


def preload_model() -> None:
    """Loads the local Whisper model up front so the cost doesn't land on
    the first real listen -- found live: the first listen_and_transcribe()
    call ate both the VAD wait AND several seconds of model loading,
    sometimes eating into the speech-detection window itself and causing a
    missed turn. No-op when USE_GROQ_STT is on -- there's no local model to
    warm up, transcription happens on Groq's hardware instead."""
    if not USE_GROQ_STT:
        _get_model()


def record_until_silence() -> np.ndarray:
    """Records from the default mic, starting once speech is detected and
    stopping automatically after TRAILING_SILENCE_MS of silence."""
    frames: list[np.ndarray] = []
    speech_flags: list[bool] = []  # per-frame, parallel to frames -- used to trim below
    speech_started = False
    frames_needed_silence = TRAILING_SILENCE_MS // FRAME_MS
    consecutive_silence_frames = 0
    start_time = time.monotonic()
    speech_first_detected_at = None
    speech_frame_count = 0
    silence_reset_count = 0  # how many times noise interrupted a silence streak
    done = False

    def callback(indata, frame_count, time_info, status):
        nonlocal speech_started, consecutive_silence_frames, done, speech_first_detected_at, speech_frame_count, silence_reset_count
        if done:
            return
        chunk = indata.copy()
        frames.append(chunk)
        is_speech = _vad.is_speech(chunk.tobytes(), SAMPLE_RATE)
        speech_flags.append(is_speech)
        if is_speech:
            speech_frame_count += 1
            if not speech_started:
                speech_first_detected_at = time.monotonic() - start_time
            speech_started = True
            if consecutive_silence_frames > 0:
                silence_reset_count += 1
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

    total_frames = len(frames)
    speech_first_str = f"{speech_first_detected_at:.1f}s" if speech_first_detected_at is not None else "jamais"
    print(f"  [diag] parole detectee apres: {speech_first_str} -- frames de parole: {speech_frame_count}/{total_frames} -- bruit ayant interrompu un silence: {silence_reset_count}x")

    if not frames:
        return np.array([], dtype=np.int16)
    return _trim_to_speech(frames, speech_flags)


# Kept around the speech so trimming never clips a soft onset or a final
# consonant -- Vietnamese tones live partly in the tail of the syllable.
# Verified at this value against the strict VAD above: across four words the
# kept window contained the full energy envelope of the speech every time,
# with margin. A permissive VAD was tried here first and is NOT the answer --
# at aggressiveness 0-2 any realistic noise floor reads as speech and nothing
# gets trimmed at all.
TRIM_PADDING_FRAMES = 300 // FRAME_MS


def _trim_to_speech(frames: list[np.ndarray], speech_flags: list[bool]) -> np.ndarray:
    """Cuts the recording down to the stretch that actually contains speech.

    Groq's transcription REST API has no server-side equivalent of local
    faster-whisper's vad_filter, so silence reaches the model as-is -- and
    Whisper hallucinates confidently on near-silence. Found live: a 2.1s clip
    that was 20/71 speech frames came back as a phrase the learner never said.
    The VAD flags are already computed frame by frame during capture, so the
    trim costs nothing.
    """
    speech_idx = [i for i, flag in enumerate(speech_flags) if flag]
    if not speech_idx:
        return np.concatenate(frames, axis=0).flatten()

    start = max(0, speech_idx[0] - TRIM_PADDING_FRAMES)
    end = min(len(frames), speech_idx[-1] + 1 + TRIM_PADDING_FRAMES)
    kept = frames[start:end]
    dropped_ms = (len(frames) - len(kept)) * FRAME_MS
    if dropped_ms:
        print(f"  [diag] silence retire avant envoi: {dropped_ms}ms ({len(kept)}/{len(frames)} frames gardees)")
    return np.concatenate(kept, axis=0).flatten()


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


def _run_transcribe(audio_float, language: str | None, initial_prompt: str | None):
    segments, info = _get_model().transcribe(
        audio_float, beam_size=5, vad_filter=True, language=language,
        initial_prompt=initial_prompt,
        # vad_filter trims silence before/around speech -- without it, silence-
        # padded recordings can make Whisper hallucinate repeated phrases
        # (seen live: "I don't know why, I don't know why...").
        vad_parameters={"min_silence_duration_ms": 500},
    )
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip(), info.language


def _load_groq_key() -> str:
    prefix = "GROQ_API_KEY="
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    raise RuntimeError("GROQ_API_KEY not found in .env")


def _audio_to_wav_bytes(audio: np.ndarray) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio.tobytes())
    return buf.getvalue()


_GROQ_LANG_NAME_TO_CODE = {"english": "en", "french": "fr", "vietnamese": "vi"}


def _run_transcribe_groq(wav_bytes: bytes, language: str | None, prompt: str | None):
    """Same shape as _run_transcribe, but offloads the compute to Groq's own
    hardware instead of this machine's CPU -- consistent with everything
    else in this project (Azure for TTS, Groq for the LLM): the goal here
    is the best learning experience, not staying 100% local like memai."""
    boundary = uuid.uuid4().hex
    parts = []
    fields = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json", "temperature": "0"}
    if language:
        fields["language"] = language
    if prompt:
        # Groq's limit (896) is in UTF-8 BYTES, not Python characters -- found
        # live: a 690-character Vietnamese string encoded to 897 bytes and
        # got rejected (HTTP 400) even though [:800] on the string looked
        # safe. Truncate the encoded bytes directly, dropping any partial
        # trailing multi-byte character so the result stays valid UTF-8.
        fields["prompt"] = prompt.encode("utf-8")[:850].decode("utf-8", errors="ignore")
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\n"
        f"Content-Type: audio/wav\r\n\r\n".encode("utf-8")
        + wav_bytes + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        data=body,
        headers={
            "Authorization": f"Bearer {_load_groq_key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        parsed = json.loads(resp.read().decode("utf-8"))
    raw_lang = parsed.get("language", "en")
    # Groq returns full language NAMES ("English"), not ISO codes like local
    # faster-whisper does -- found live: comparing "English" against
    # ALLOWED_LANGUAGES={"vi","en","fr"} was always False, so the "redundant
    # second pass" guard below never actually skipped, silently doubling
    # Whisper compute on every single turn even when the first pass was fine.
    lang = _GROQ_LANG_NAME_TO_CODE.get(raw_lang.strip().lower(), raw_lang.strip().lower())
    return parsed.get("text", "").strip(), lang


# Groq's own hardware runs whisper-large-v3-turbo, bigger and faster than the
# local "small" CPU model -- consistent with the rest of the project (Azure
# for TTS, Groq for the LLM): the priority is the learning experience, not
# staying 100% local the way memai does. Toggle back to False to compare.
USE_GROQ_STT = True


def transcribe(audio: np.ndarray) -> tuple[str, str]:
    """Returns (text, language_code), language_code always in ALLOWED_LANGUAGES.

    Deliberately reports what was actually said, with no correction pass of
    any kind. A vocabulary hint used to be fed to the decoder to pull mangled
    attempts onto known words; measurement killed it (four seconds of pure
    noise came back as "ừ ừ ừ ừ ừ", and it turned a correct "tôi" into "tốt").
    Snapping the text afterwards was tried too and rejected on purpose: it
    repairs mispronunciation, which is the very thing the tutor needs to see.
    Judging how far off an attempt is belongs to the tutor, not here.
    """
    if audio.size == 0:
        return "", "en"
    print(f"  [diag] audio enregistre: {len(audio) / SAMPLE_RATE:.1f}s")
    t0 = time.monotonic()
    if USE_GROQ_STT:
        wav_bytes = _audio_to_wav_bytes(audio)
        text, lang = _run_transcribe_groq(wav_bytes, language=None, prompt=None)
        print(f"  [diag] 1ere passe groq stt: {time.monotonic() - t0:.1f}s (langue detectee: {lang})")
        if lang not in ALLOWED_LANGUAGES:
            t1 = time.monotonic()
            text, _ = _run_transcribe_groq(wav_bytes, language="vi", prompt=None)
            print(f"  [diag] 2eme passe groq stt (langue forcee vi): {time.monotonic() - t1:.1f}s")
            lang = "vi"
        return text, lang

    audio_float = audio.astype(np.float32) / 32768.0
    text, lang = _run_transcribe(audio_float, language=None, initial_prompt=None)
    print(f"  [diag] 1ere passe whisper: {time.monotonic() - t0:.1f}s (langue detectee: {lang})")
    if lang not in ALLOWED_LANGUAGES:
        # Auto-detect landed on something nonsensical for this context (seen
        # live: literal Japanese/Korean script from a mangled pronunciation
        # attempt) -- clamping just the language TAG before left the actual
        # transcribed text in that foreign script, useless to the tutor.
        # Re-run forcing Vietnamese phonetics instead of trusting the guess.
        t1 = time.monotonic()
        text, _ = _run_transcribe(audio_float, language="vi", initial_prompt=None)
        print(f"  [diag] 2eme passe whisper (langue forcee vi): {time.monotonic() - t1:.1f}s")
        lang = "vi"
    return text, lang


# Found live: forgetting the second Enter press to STOP recording leaves
# the program blocked on input(), looking exactly like "nothing happens."
# Hands-free (VAD auto-stop) avoids that whole class of confusion.
USE_PUSH_TO_TALK = False


def listen_and_transcribe() -> str:
    """Full turn: listen (push-to-talk or hands-free per USE_PUSH_TO_TALK),
    transcribe, return a [lang:xx]-tagged string."""
    audio = record_until_enter() if USE_PUSH_TO_TALK else record_until_silence()
    text, lang = transcribe(audio)
    if not text:
        return ""
    return f"[lang:{lang}] {text}"
