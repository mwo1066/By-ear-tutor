"""Azure TTS synthesis + playback, with automatic voice routing by language.

Vietnamese text (heavy diacritics) -> the Vietnamese teacher voice.
Everything else -> the tutor's own (English) voice.
Splits the LLM's response into runs of consecutive same-language text so
each run is spoken by the correct voice, matching the two-voice cast rule.
"""
import re
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
# marks). NOT Vietnamese-specific on its own -- French shares six of these
# accented letters (à, â, é, è, ê, ô), so once the tutor speaks French to a
# French-speaking learner, plain French words like "après"/"être" would
# false-positive here. Everything else in this range (the extra letters
# ă/ơ/ư/đ, and any hook-above/tilde/dot-below tone, or acute/grave on i/o/u/y)
# never occurs in French -- that subset is used as the exclusive signal below.
_VN_BROAD_CHAR = re.compile("[à-ỹĐđ]")
_FRENCH_SHARED_CHARS = set("àâéèêôÀÂÉÈÊÔ")


def _has_exclusive_vn_marker(word: str) -> bool:
    """True if word contains a diacritic that never appears in French --
    the reliable signal once the learner's own language might also use
    accented Latin characters (unlike English, where any diacritic at all
    used to be a safe signal)."""
    return any(_VN_BROAD_CHAR.match(ch) and ch not in _FRENCH_SHARED_CHARS for ch in word)


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
    """Three signals, strongest first: (1) it's literally a word from our
    own roster/generated content -- we author every Vietnamese word
    ourselves, so this is the most reliable check and the only one immune
    to the French/Vietnamese diacritic overlap; (2) it carries a diacritic
    that's exclusively Vietnamese (never appears in French); (3) it's one
    of the known bare-ASCII exceptions."""
    lw = word.lower()
    if lw in known_vn_words:
        return True
    return _has_exclusive_vn_marker(word) or lw in _VN_BARE_WORDS


_TOKEN_RE = re.compile(r"\S+|\s+")


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
    tokens = _TOKEN_RE.findall(text.strip())
    runs: list[tuple[str, str]] = []
    for tok in tokens:
        if tok.isspace():
            if runs:
                runs[-1] = (runs[-1][0], runs[-1][1] + tok)
            continue
        match = _WORD_RE.search(tok)
        key = "teacher" if match and _is_vietnamese_word(match.group(), known_vn_words) else "tutor"
        if runs and runs[-1][0] == key:
            runs[-1] = (key, runs[-1][1] + tok)
        else:
            runs.append((key, tok))
    return [(key, chunk.strip()) for key, chunk in runs if chunk.strip()]


_MARKDOWN_CHARS = re.compile(r"[*_#`~]")


def _strip_markdown(text: str) -> str:
    """Defensive backstop: the model keeps writing **word** despite being
    told not to, twice now -- stop relying on the prompt and just strip it
    before anything reaches TTS, so a literal asterisk never gets spoken."""
    return _MARKDOWN_CHARS.sub("", text)


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
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.read()
        except _TTS_ERRORS as e:
            if attempt < retries - 1:
                print(f"  (Azure TTS: {e} -- nouvel essai...)")
                continue
            print(f"  (Azure TTS indisponible apres {retries} essais ({e}) -- ce passage ne sera pas dit a voix haute)")
            return None


def speak(text: str, known_vn_words: frozenset[str] = frozenset()) -> None:
    """Splits text by voice, synthesizes each run, plays them back in order."""
    for voice_key, chunk in split_by_voice(text, known_vn_words):
        audio = synthesize(chunk, voice_key)
        if audio is None:
            continue
        tmp_path = Path(__file__).parent / "voices" / "_playback.wav"
        tmp_path.write_bytes(audio)
        winsound.PlaySound(str(tmp_path), winsound.SND_FILENAME)
