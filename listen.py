"""Microphone capture with automatic silence detection, transcribed on Groq.

webrtcvad frame by frame: waits for speech to start, keeps recording through
it, stops after a stretch of trailing silence. No key to press to end a turn.

The local faster-whisper path that used to sit alongside this is gone. It had
not run since Groq STT became the default, cost 1.3s of import on every start,
and was where a vad_filter fix quietly stopped applying -- a fallback nobody
exercises is not a fallback. It is in git history if it is ever wanted back.
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

ENV_PATH = Path(__file__).parent / ".env"

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480 samples/frame at 16kHz/30ms

VAD_AGGRESSIVENESS = 3            # max strictness; see the note on the gate below
TRAILING_SILENCE_MS = 1200        # stop after this much silence once speech has started
MAX_WAIT_FOR_SPEECH_S = 10        # give up if nobody starts talking
MAX_RECORDING_S = 30              # hard safety cap

# A frame counts as speech only if BOTH the voice detector and the loudness gate
# agree, because each is blind to a different kind of noise.
#
# Measured on a laptop with a loud fan: webrtcvad at its strictest called 93% of
# SILENCE speech, and 91% of a spoken word -- silence scored higher than the
# voice. It is built for telephony and steady broadband noise sits inside the
# band it listens to, so no aggressiveness setting separates them.
#
# The same recording separated cleanly by loudness: room 286 rms, spoken word
# 1117, with peaks 15x apart. So loudness supplies what the detector cannot.
# The reverse is also true -- a door slam is loud but is not a voice -- which is
# why this is an AND rather than a replacement.
#
# The floor is measured continuously rather than fixed, so the same rule works
# in a silent room and next to a fan: speech is the loud minority of recent
# frames, so a low percentile of them is the room itself.
ENERGY_RATIO = 3.0                # a frame must be this much louder than the room
ENERGY_FLOOR_PERCENTILE = 20      # of recent frames -- the room, not the voice
ENERGY_WINDOW_FRAMES = 100        # ~3s of history to measure the room from
ENERGY_ABSOLUTE_MIN = 120.0       # keeps a very quiet room from arming a hair trigger

_vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)


def _frame_energy(chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))


def _speech_threshold(recent: list[float]) -> float:
    """How loud a frame must be, right now, in this room."""
    if not recent:
        return ENERGY_ABSOLUTE_MIN
    floor = float(np.percentile(recent, ENERGY_FLOOR_PERCENTILE))
    return max(floor * ENERGY_RATIO, ENERGY_ABSOLUTE_MIN)


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
    recent_energy: list[float] = []
    vad_only_count = 0  # frames the detector called speech but the room explains

    def callback(indata, frame_count, time_info, status):
        nonlocal speech_started, consecutive_silence_frames, done, speech_first_detected_at, speech_frame_count, silence_reset_count, vad_only_count
        if done:
            return
        chunk = indata.copy()
        frames.append(chunk)

        energy = _frame_energy(chunk)
        threshold = _speech_threshold(recent_energy)
        recent_energy.append(energy)
        del recent_energy[:-ENERGY_WINDOW_FRAMES]

        vad_says = _vad.is_speech(chunk.tobytes(), SAMPLE_RATE)
        loud_enough = energy >= threshold
        is_speech = vad_says and loud_enough
        if vad_says and not loud_enough:
            vad_only_count += 1
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

    print("  [listening -- speak now. Do NOT press Enter, it stops on its own when you go quiet]")
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
    speech_first_str = f"{speech_first_detected_at:.1f}s" if speech_first_detected_at is not None else "never"
    gated = f" -- room noise gated out: {vad_only_count}" if vad_only_count else ""
    print(f"  [diag] speech after: {speech_first_str} -- speech frames: {speech_frame_count}/{total_frames} -- noise breaking a silence: {silence_reset_count}x{gated}")

    if not frames:
        return np.array([], dtype=np.int16)
    # An empty return is a supported outcome all the way up: transcribe returns
    # "", listen_and_transcribe returns "", and the lesson loop simply listens
    # again without consuming the step.
    if speech_frame_count < MIN_SPEECH_FRAMES:
        print(f"  [diag] too little speech to transcribe: {speech_frame_count} frame(s) "
              f"-- nothing sent, Whisper would have invented a sentence")
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

# Below this many speech frames there is nothing to transcribe, and sending it
# anyway is worse than sending nothing: Whisper does not return empty on
# silence, it invents. Found live at 1 speech frame out of 126 -- the padding
# alone built a 0.6s window around it, which came back as
# "ありがとうございました", Whisper's single most common hallucination
# (a YouTube sign-off learned over silent outros). The tutor then scored it as
# a missed word and bumped the level.
#
# Five frames is 150ms. Measured on this microphone, a real one-word answer
# lands at 13+ frames ("tôi" -> 13/70, transcribed "Tua"), so this sits well
# under any genuine syllable and well over the noise that produces a
# hallucination. Raise it first if invented words keep arriving.
MIN_SPEECH_FRAMES = 5


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
        print(f"  [diag] silence trimmed before upload: {dropped_ms}ms ({len(kept)}/{len(frames)} frames kept)")
    return np.concatenate(kept, axis=0).flatten()


# Only languages that actually make sense here: the target language, and the
# one the session is conducted in. Whisper's full language auto-detect will
# happily guess Polish or Japanese from a few unclear syllables -- found live,
# attempts at "tôi" got tagged [lang:pl]/[lang:ja]. Anything outside this set
# almost certainly means "mangled pronunciation attempt", which the persona
# prompt already knows how to handle -- so it gets normalized to "vi" instead
# of passing through a meaningless exotic tag.
#
# French was in this set and is deliberately out: the session is English and
# Vietnamese, nothing else. It bought nothing and it cost a real failure --
# a mangled attempt at a Vietnamese word came back tagged [lang:fr] with its
# French text intact, passed straight through to the tutor, and had it answer
# in French mid-lesson. The same audio now takes the forced-Vietnamese second
# pass, which is what it should always have been.
ALLOWED_LANGUAGES = {"vi", "en"}


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

# The full model, not the turbo one. Turbo buys speed with accuracy, and the
# speed is worth nothing here: transcription takes ~0.3s inside a turn that
# runs 4-15s, almost all of it speech synthesis. So the trade was paying
# accuracy for about 3% of a turn -- on the hardest input this system sees, a
# one-second clip of a beginner's Vietnamese through a noisy room.
#
# What that cost, measured on one live session: "The", "T", "D", "E.",
# "HACTION", "Geksen" -- and "D" scoring 0.67 against "đi", so a single letter
# was recorded as a correct answer and pushed the word down the review odds.
# Every verdict the tutor gives rests on this, so it is the wrong place to be
# saving a third of a second.
STT_MODEL = "whisper-large-v3"


def _run_transcribe_groq(wav_bytes: bytes, language: str | None, prompt: str | None):
    """Same shape as _run_transcribe, but offloads the compute to Groq's own
    hardware instead of this machine's CPU -- consistent with everything
    else in this project (Azure for TTS, Groq for the LLM): the goal here
    is the best learning experience, not staying 100% local like memai."""
    boundary = uuid.uuid4().hex
    parts = []
    fields = {"model": STT_MODEL, "response_format": "verbose_json", "temperature": "0"}
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
# Beyond this many words, an utterance is a sentence rather than an attempt at
# a vocabulary item -- almost always a question in the learner's own language.
SENTENCE_WORDS = 3

# How many words count as the learner speaking rather than attempting a word.
# ONE number, for every language the decoder might name -- because the name
# carries no information either way. Measured 17 August: "too fast" was tagged
# ITALIAN, so a floor that only applied to English never fired, and it was
# forced into Vietnamese as "TÙ PHÁST". The tags this microphone produced across
# two sessions: Italian, Russian, German, Spanish, Turkish, Korean, Dutch,
# Portuguese, Chinese -- for a voice speaking only English and Vietnamese.
#
# Two, not four: "I forgot" and "too fast" are the commonest interruptions there
# are. It is only this low because the resemblance veto in is_learner_talking
# catches the attempts that would otherwise fall in.
SPEECH_WORDS = 2


def is_learner_talking(text: str, lang: str, expected: str = "", resembles=None) -> bool:
    """The learner is addressing the tutor, not attempting the word the lesson
    is waiting for.

    `resembles(text, expected)` is passed in, like `matches`, so this module
    stays unaware of the tutor. Without it the similarity veto below cannot run
    and a mangled two-word attempt is kept as heard instead of recovered -- the
    cheap direction, but say so rather than let it pass silently.

    Guards the worst failure this system has produced. Live, on a step
    expecting "tôi": the learner said, in clear English, "No, I'm asking for
    travel, listen, I don't care what I am me." That does not contain "tôi", so
    a forced-Vietnamese second pass ran and returned
    "Không, tôi đang chờ đề lý, nghe, tôi không quanh gì tôi là." -- invented
    Vietnamese that happens to contain "tôi". The recovery test is only "does
    it contain the expected word", so the invention was accepted, scored as a
    correct answer, and the lesson moved on. The learner was objecting and was
    told "Exactly."

    Getting this wrong the other way is cheap: a long Vietnamese attempt heard
    as English is marked missed and asked again. Getting it wrong this way
    overwrites what the learner actually said.

    Keyed on "not Vietnamese" rather than "English", because the same failure
    came back on 13 August wearing a different label. The learner asked out
    loud for the answer to be given to them. Pass 1 decoded that as KOREAN, so
    `lang == "en"` was false, the guard never fired, a forced-Vietnamese pass
    invented "Tôi... Chị... Giờ giải thích cho tôi", and the lesson received
    that behind a [lang:vi] tag as though it were an attempt.

    So the label was not trusted on its own and a length test was put in front of
    it -- more than three words. That protected the attempts by sacrificing the
    short interruptions, and the cost was never written down. Measured 17 August
    into this microphone: "I forgot" (2 words), "I didn't understand" (3), "Can
    you repeat that?" read as "You repeat that." (3). None fired the guard, so
    the forced pass ran and TRANSLATED them -- "I didn't understand" came back
    "Toi khong hieu.", which contains both `toi` and `khong` and scores a correct
    answer on any step asking for either. The learner says they did not
    understand and is told "Exactly."

    Neither length nor language separates the two groups: what has to be
    protected is 2-3 words ("I forgot.", "You repeat that.") and what has to be
    recovered is 1-2 ("toi", "Fen Bey.", "and Bay"), all tagged English.

    What does separate them is that **an attempt looks like the word that was
    asked for** and a sentence does not. Recorded attempts score 0.571, 0.857 and
    1.000 against their target; English of two words or more tops out at 0.308.
    So similarity is the veto, and the length test only sets the floor at which
    English counts as speech at all.

    That floor is two words, not one, and deliberately: single-word English is
    left exactly as it was. It is where a badly heard attempt lives -- "Bye!" for
    tôi scores 0.000, resembling nothing, and must still reach the forced pass.
    The course asks for single words constantly, so one-word recovery is worth
    more than protecting a one-word interruption.

    Both mistakes stay possible; they do not cost the same, and the threshold is
    set by the expensive one:

        attempt taken for speech -> marked missed, asked again (rules 20, 4c-bis)
        speech taken for an attempt -> translated, SCORED CORRECT, level raised
    """
    if lang == "vi":
        return False
    if expected and resembles is not None and resembles(text, expected):
        return False
    return len(text.split()) >= SPEECH_WORDS


def transcribe(audio: np.ndarray, expected: str | None = None, matches=None,
               resembles=None) -> tuple[str, str]:
    """Returns (text, language_code), language_code always in ALLOWED_LANGUAGES.

    `expected` is the Vietnamese word the lesson is waiting for, when it is
    waiting for one, and `matches(text, expected)` decides whether it arrived.
    Both are passed in rather than imported so this module stays unaware of the
    tutor.

    Never repairs what was said: a vocabulary hint fed to the decoder made
    Whisper invent Vietnamese out of pure noise, and snapping the text onto the
    nearest known word erased the mispronunciation the tutor is meant to hear.
    Choosing which language to decode in is a different thing -- it changes how
    the audio is read, not what it is turned into afterwards.
    """
    if audio.size == 0:
        return "", "en"
    print(f"  [diag] audio recorded: {len(audio) / SAMPLE_RATE:.1f}s")
    t0 = time.monotonic()
    wav_bytes = _audio_to_wav_bytes(audio)
    text, lang = _run_transcribe_groq(wav_bytes, language=None, prompt=None)
    print(f"  [diag] groq stt pass 1: {time.monotonic() - t0:.1f}s (detected language: {lang})")

    # The lesson is waiting for a specific Vietnamese word, so if auto-detect
    # did not produce it, ask again for that language explicitly. Found live:
    # "tên" was heard correctly but written with English spelling, and came out
    # as the digits "10" -- right sound, unusable text.
    if expected and matches and not matches(text, expected):
        if is_learner_talking(text, lang, expected or "", resembles):
            # They are speaking to the tutor, not attempting the word. Forcing
            # this into Vietnamese does not recover anything -- it destroys the
            # only true record of what was said.
            if lang != "en":
                # Pass 1 was lost in some third language, so ITS text is not a
                # reading of what was said either -- keeping it would hand the
                # tutor Korean. Decoding as English is what the no-expected
                # branch below already does with a long utterance.
                text = _forced(wav_bytes, "en", t0)
            # …and now that we have a reading in a language we can judge, ask
            # again whether it is really speech. An English decode of a
            # Vietnamese SENTENCE comes back as English-looking nonsense that
            # still traces the target: seen in session, "Tôi tên là Anna" was
            # tagged Korean, decoded to "Totten-Lay-Anna." and handed to the
            # tutor as a question -- so it answered with the sentence the
            # learner had just produced correctly.
            if expected and resembles is not None and resembles(text, expected):
                second = _forced(wav_bytes, "vi", t0)
                print(f"  [diag] English reading traces {expected!r} -- it was the answer: {text!r} -> {second!r}")
                return second, "vi"
            print(f"  [diag] a sentence, not an attempt at {expected!r} -- kept as heard")
            return text, "en"
        second = _forced(wav_bytes, "vi", t0)
        if matches(second, expected):
            print(f"  [diag] pass 2 recovered it: {text!r} -> {second!r}")
            return second, "vi"
        if lang in ALLOWED_LANGUAGES:
            return text, lang
        # Pass 1 decoded into a language this session does not have, so its text
        # is not a reading of what was said -- it is the decoder lost. The
        # forced-Vietnamese pass at least read the audio as the language it was
        # meant to be, so it is the one kept, exactly as the no-expected branch
        # below already does. Keeping pass 1 here instead put Japanese text
        # behind a [lang:vi] tag: an attempt at "tôi" arrived as
        # "ありがとうございました" wearing a Vietnamese label.
        # Still not repairing anything -- choosing the decode language changes
        # how the audio is READ, never what the text is turned into afterwards.
        return second, "vi"

    if lang not in ALLOWED_LANGUAGES:
        # An unexpected language means the decoder was lost. Which way to push
        # it depends on length: one or two words is an attempt at a vocabulary
        # item, a whole sentence is a question. Forcing everything to Vietnamese
        # turned "how do you say dog in Vietnamese?" into "Cái cách nói đáy ở
        # Việt Nam?", and the tutor taught the word for "bottom".
        forced = "vi" if len(text.split()) <= SENTENCE_WORDS else "en"
        return _forced(wav_bytes, forced, time.monotonic()), forced
    return text, lang


def _forced(wav_bytes: bytes, language: str, since: float) -> str:
    t = time.monotonic()
    text, _ = _run_transcribe_groq(wav_bytes, language=language, prompt=None)
    print(f"  [diag] groq stt pass 2 (forced {language}): {time.monotonic() - t:.1f}s")
    return text


def listen_and_transcribe(expected: str | None = None, matches=None, resembles=None) -> str:
    """Full turn: listen hands-free, transcribe, return a [lang:xx]-tagged string."""
    audio = record_until_silence()
    text, lang = transcribe(audio, expected=expected, matches=matches, resembles=resembles)
    if not text:
        return ""
    return f"[lang:{lang}] {text}"
