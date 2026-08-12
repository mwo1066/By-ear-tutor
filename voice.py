"""Azure TTS synthesis + playback, with automatic voice routing by language.

Vietnamese text (heavy diacritics) -> the Vietnamese teacher voice.
Everything else -> the tutor's own (English) voice.
Splits the LLM's response into runs of consecutive same-language text so
each run is spoken by the correct voice, matching the two-voice cast rule.
"""
import queue
import re
import threading
from concurrent.futures import Future, ThreadPoolExecutor
import winsound
import urllib.request
import urllib.error
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ENV_PATH = Path(__file__).parent / ".env"

TUTOR_VOICE = ("en-US-AmandaMultilingualNeural", "Female", "en-US")
TEACHER_VOICE = ("vi-VN-NamMinhNeural", "Male", "vi-VN")

# Slower than default -- found live: the intro (3 rules) went by too fast to
# actually absorb. Negative percentage = slower via SSML prosody rate.
SPEECH_RATE = "-15%"

# Broad Vietnamese-ish diacritic range (Latin Extended-A/B + combining tone
# marks). The tutor's own half of the session is English, which carries no
# diacritics at all, so any accented letter in this range is Vietnamese.
#
# This used to carve out the six letters French shares (à, â, é, è, ê, ô),
# from when the tutor might speak French and "après"/"être" would false
# positive. That carve-out is gone with French: it was what forced "là" to be
# recognised by roster lookup instead of by its own accent, so a Vietnamese
# word not yet in the roster -- one the learner just asked about -- came out
# of the English voice.
_VN_BROAD_CHAR = re.compile("[à-ỹĐđ]")


def _has_vn_marker(word: str) -> bool:
    """True if the word carries any Vietnamese diacritic."""
    return any(_VN_BROAD_CHAR.match(ch) for ch in word)


# Common Vietnamese words that happen to have NO diacritics at all (bare
# ASCII spelling) -- found live: "anh"/"em"/"ngon" from our own roster were
# misrouted to the English voice because the diacritic check alone missed
# them. Deliberately NOT adding ambiguous words that are also real English
# words (e.g. "ban") -- that would misroute genuine English sentences.
# Extend only with words confirmed in our own roster (see content.py).
_VN_BARE_WORDS = {"anh", "em", "ngon"}
_WORD_RE = re.compile(r"[a-zà-ỹđ]+", re.IGNORECASE)


def _load_env() -> dict:
    with open(ENV_PATH, encoding="utf-8") as f:
        return dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))


def _is_vietnamese_word(word: str, known_vn_words: frozenset[str]) -> bool:
    """Three signals: (1) it carries a Vietnamese diacritic, which in an
    English-only session is conclusive and works for words the course has
    not reached yet; (2) it's literally a word from our own roster/generated
    content; (3) it's one of the known bare-ASCII exceptions."""
    lw = word.lower()
    if _has_vn_marker(word):
        return True
    return lw in known_vn_words or lw in _VN_BARE_WORDS


# The voice is decided per WORD, never per whitespace-separated token. Found
# live: the model wrote "That's correct—là." with no space around the dash, so
# "correct—là." arrived as ONE token; the classifier looks at the first run of
# letters it finds, saw "correct", and sent the whole token -- the Vietnamese
# word with it -- to the English voice. Minh never spoke, and a tonal word was
# read aloud by the one voice that cannot say it.
#
# Splitting on the words themselves makes the punctuation irrelevant instead of
# dangerous: it simply rides along with the run before it. That covers the em
# dash, the slash, brackets, and every other glue character without naming any
# of them -- the previous shape needed a new one noticed per session.
_WORD_SPLIT_RE = re.compile(r"([a-zà-ỹđ]+)", re.IGNORECASE)


def split_by_voice(text: str, known_vn_words: frozenset[str] = frozenset()) -> list[tuple[str, str]]:
    """Splits text into (voice_key, chunk) runs, voice_key in {"teacher","tutor"}.
    Word-level, not sentence-level -- found live: a whole sentence like
    "Repeat after the teacher: tôi." is mostly English with one embedded
    Vietnamese word, and sentence-level classification (even majority-vote)
    puts the ENTIRE sentence in one voice, so the tutor's own voice ends up
    mispronouncing "tôi" instead of handing that one word to the teacher.
    Consecutive words of the same language are merged into a single run
    (so a whole genuinely-Vietnamese sentence still becomes one clip, not
    one clip per word) but the boundary moves the instant the language does.
    known_vn_words should be every word appearing in the current roster's
    item names, so genuine Vietnamese vocabulary is recognized regardless of
    what language the tutor's own voice happens to be using this session."""
    # re.split with a capturing group alternates: even indices are the gaps
    # between words (spaces, punctuation), odd indices are the words themselves.
    parts = _WORD_SPLIT_RE.split(text.strip())
    runs: list[tuple[str, str]] = []
    pending = ""  # punctuation seen before any word -- joins whichever run opens
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 0:  # a gap: it belongs to the run it follows
            if runs:
                runs[-1] = (runs[-1][0], runs[-1][1] + part)
            else:
                pending += part
            continue
        key = "teacher" if _is_vietnamese_word(part, known_vn_words) else "tutor"
        if runs and runs[-1][0] == key:
            runs[-1] = (key, runs[-1][1] + part)
        else:
            runs.append((key, pending + part))
            pending = ""
    # A capitalised unaccented word that CONTINUES a Vietnamese run, with no
    # sentence break in between, is a proper name inside that sentence. "Em tên
    # là Nam." was coming out as Minh saying "Em tên là" and the English voice
    # finishing with "Nam", mid-phrase.
    #
    # A property rather than a list of names: proper nouns carry no diacritics
    # and there is no end to them, so _VN_BARE_WORDS could never cover them --
    # and filling it with ambiguous bare words is exactly what made Minh
    # pronounce "So" and "Do" earlier today. Capitalisation and adjacency are
    # what actually distinguish a name here, and a sentence break ends the claim:
    # "... is tên. Now you say it." keeps "Now" with the tutor.
    merged: list[tuple[str, str]] = []
    for key, chunk in runs:
        if (merged and merged[-1][0] == "teacher" and key == "tutor"
                and not any(c in merged[-1][1] for c in ".!?")
                and len(chunk.split()) == 1 and chunk.strip(" .,!?").istitle()):
            merged[-1] = ("teacher", merged[-1][1] + chunk)
            continue
        merged.append((key, chunk))
    runs = merged

    if not runs and pending.strip():
        # No letters at all -- digits, or punctuation on its own. Still the
        # tutor's to say: dropping it would silently swallow "1975".
        return [("tutor", pending.strip())]
    return [(key, chunk.strip()) for key, chunk in runs if chunk.strip()]


_MARKDOWN_CHARS = re.compile(r"[*_#`~]")

# Stage directions the model writes despite the cast rules saying voices are
# routed automatically: "Minh: tôi." makes the English voice announce "Minh"
# before the word. Same class of problem as the markdown above -- the prompt
# says don't, the model does it anyway, so strip it rather than argue.
_SPEAKER_LABEL = re.compile(r"^\s*(minh|tutor|teacher|tuteur|prof)\s*:\s*", re.IGNORECASE)

# The regex above only catches the name used as a PREFIX, and only with a
# colon. Cueing Minh is a stage direction the model writes however it likes:
# "Minh: tôi." one session, a bare "Minh." the next -- which slipped straight
# through, so the English voice announced "Minh" before each of the teacher's
# lines, twice in one lesson.
#
# Adding the full stop to the regex would fix that session and not the next
# one ("Minh —", "(Minh)"). The list of punctuation is open and grows every
# time; "the line is nothing but a name" is a rule that cannot grow, because
# the cast is closed at two voices. That is the whole difference.
_SPEAKER_NAMES = frozenset({"minh", "tutor", "teacher", "tuteur", "prof"})


def is_stage_direction(text: str) -> bool:
    """True if the line carries nothing but a speaker's name."""
    letters = "".join(c if c.isalpha() else " " for c in text.lower())
    return " ".join(letters.split()) in _SPEAKER_NAMES


def _strip_markdown(text: str) -> str:
    """Defensive backstop: the model keeps writing **word** despite being
    told not to, twice now -- stop relying on the prompt and just strip it
    before anything reaches TTS, so a literal asterisk never gets spoken."""
    return _SPEAKER_LABEL.sub("", _MARKDOWN_CHARS.sub("", text))


# ---------------------------------------------------------------------------
# Two properties of anything about to be spoken, checked in the one place every
# line passes through. Not more entries in a list of known-bad strings: the same
# two CLASSES of fault have each been fixed twice this project, at a different
# call site each time, because the fix was applied where the bug was noticed
# rather than where speech leaves.
# ---------------------------------------------------------------------------

# Authoring notation: "+ [động từ]", "[tên riêng]", "___". A stored item name
# carries it; speech never should. Seen twice, and heard both times -- the retry
# line said "Listen again — tôi tên là + [tên riêng]" and the acknowledgement
# said "It was muốn + [động từ]", which Minh recited as "muốn động từ".
_AUTHORING_NOTATION = re.compile(r"\s*\+?\s*\[[^\]]*\]|_{2,}")


def _strip_authoring_notation(text: str) -> str:
    """Removes what belongs to the content files and not to a sentence.

    Repaired rather than merely reported, because the repair is exact: a
    placeholder is never speech under any circumstance. The log line is what
    makes the real bug visible upstream.
    """
    cleaned = _AUTHORING_NOTATION.sub("", text)
    if cleaned != text:
        print(f"  (authoring notation stripped before speech: {text!r})")
    return " ".join(cleaned.split())


def _warn_if_english_reaches_minh(text: str, known_vn_words: frozenset[str]) -> None:
    """Minh should never be handed a word with no Vietnamese in it.

    Every teacher run ought to carry a diacritic, or be one of the few vetted
    bare-ASCII words. When a frequency list was imported, the routing vocabulary
    silently gained so/do/ta/con/ra, and the tutor's own "So how would you say
    it?" came out with Minh pronouncing "So" -- a random Vietnamese syllable in
    the middle of an English sentence. Reported, not repaired: the fix belongs
    in whatever fed that vocabulary, and guessing here would hide it.
    """
    for key, chunk in split_by_voice(text, known_vn_words):
        if key != "teacher":
            continue
        words = _WORD_RE.findall(chunk)
        if words and not any(_has_vn_marker(w) or w.lower() in _VN_BARE_WORDS for w in words):
            print(f"  [diag] !! Minh was handed {chunk!r}, which carries no Vietnamese")


_TTS_ERRORS = (urllib.error.URLError, TimeoutError, OSError)


def synthesize(text: str, voice_key: str, retries: int = 2) -> bytes | None:
    """Returns None (instead of raising) once all retries are exhausted --
    a transient Azure hiccup should skip that one chunk of speech, not
    crash the whole session."""
    text = _strip_markdown(text)
    env = _load_env()
    name, gender, locale = TEACHER_VOICE if voice_key == "teacher" else TUTOR_VOICE
    ssml = (
        f"<speak version='1.0' xml:lang='{locale}'>"
        f"<voice xml:lang='{locale}' xml:gender='{gender}' name='{name}'>"
        f"<prosody rate='{SPEECH_RATE}'>{xml_escape(text)}</prosody>"
        f"</voice></speak>"
    )
    req = urllib.request.Request(
        f"https://{env['AZURE_SPEECH_REGION']}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": env["AZURE_SPEECH_KEY"],
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "viet-tutor",
        },
        method="POST",
    )
    for attempt in range(retries):
        try:
            # 15s, not 8: measured cold-connection clips legitimately take
            # 4-5s, and an 8s ceiling was dropping real speech on the floor.
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read()
        except _TTS_ERRORS as e:
            if attempt < retries - 1:
                print(f"  (Azure TTS: {e} -- retrying...)")
                continue
            print(f"  (Azure TTS unavailable after {retries} attempts ({e}) -- this passage will not be spoken)")
            return None


_WAV_MIN_BYTES = 128  # a RIFF header alone is 44; anything near that carries no speech
_EMPTY_WAV_BYTES = 64  # at or under this it is just a header: silence, by design


def _is_playable_wav(audio: bytes) -> bool:
    """Cheap sanity check before handing bytes to the sound driver."""
    return len(audio) >= _WAV_MIN_BYTES and audio[:4] == b"RIFF" and audio[8:12] == b"WAVE"


class SpeechPipeline:
    """Synthesizes the next clip while the current one is still playing.

    Speaking used to be strictly serial -- synthesize, play, synthesize, play --
    so every gap between two spoken sentences was a full Azure round trip of
    dead air, varying with Azure's load. Found live: a seven-sentence opening
    turn took 44s of which the model accounted for 1s. Here synthesis stays
    ahead of playback, so only the very first clip pays that cost.

    Synthesis runs on a POOL, not a single worker. Measured against Azure:
    per-clip latency is bimodal (0.27s when a connection is warm, 4-5s when a
    new one has to be established), so one worker stalls on every cold clip.
    Seven clips took 31s serially against 6.9s across four workers. Playback
    stays strictly serial and in order -- only synthesis fans out.
    """

    SYNTH_WORKERS = 4

    def __init__(self, known_vn_words: frozenset[str] = frozenset()):
        self._known_vn_words = known_vn_words
        self._pool = ThreadPoolExecutor(max_workers=self.SYNTH_WORKERS)
        self._to_play: "queue.Queue[Future]" = queue.Queue()
        self._playback_path = Path(__file__).parent / "voices" / "_playback.wav"
        threading.Thread(target=self._play_loop, daemon=True).start()

    def _play_loop(self) -> None:
        while True:
            future = self._to_play.get()
            try:
                audio = future.result()
                if audio is None:  # Azure gave up; skip, don't hang
                    pass
                elif not _is_playable_wav(audio):
                    # Azure occasionally answers 200 with a body that is not
                    # audio (an error document, or a truncated stream). Caught
                    # here rather than handed to PlaySound, which would fall
                    # back to the Windows default chime -- the mystery "ding"
                    # heard mid-lesson was exactly this.
                    # A bare header is the ordinary case, not a fault: a
                    # stripped "Minh:" stage direction leaves an empty string,
                    # and Azure dutifully returns silence. Nothing is lost, so
                    # it is not worth a line of log every single turn.
                    if len(audio) > _EMPTY_WAV_BYTES:
                        print(f"  (invalid audio skipped: {len(audio)} bytes)")
                else:
                    self._playback_path.write_bytes(audio)
                    winsound.PlaySound(
                        str(self._playback_path),
                        winsound.SND_FILENAME | winsound.SND_NODEFAULT,
                    )
            except Exception as e:
                print(f"  (playback skipped: {e})")
            finally:
                self._to_play.task_done()

    def say(self, text: str) -> None:
        """Queues text for speech and returns immediately.

        Submitting to the pool starts synthesis at once, so by the time the
        playback thread reaches a clip its audio is usually already in hand.
        """
        text = _strip_authoring_notation(text)
        _warn_if_english_reaches_minh(text, self._known_vn_words)
        if is_stage_direction(text):
            # Dropped here rather than sent as an empty string: no Azure round
            # trip, and the log says plainly that the model wrote one.
            print(f"  (stage direction, not spoken: {text!r})")
            return
        for voice_key, chunk in split_by_voice(text, self._known_vn_words):
            self._to_play.put(self._pool.submit(synthesize, chunk, voice_key))

    def wait(self) -> None:
        """Blocks until everything queued has actually finished playing --
        must be called before opening the mic, or it records our own voice."""
        self._to_play.join()
