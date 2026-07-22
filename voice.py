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

# Vietnamese-specific diacritic range (covers all 6 tones + special vowels).
_VN_CHARS = re.compile(
    "[à-ỹĐđ]"  # broad Latin Extended-A/B + combining tone marks
)

# Common Vietnamese words that happen to have NO diacritics at all (bare
# ASCII spelling) -- found live: "anh"/"em"/"ngon" from our own roster were
# misrouted to the English voice because the diacritic check alone missed
# them. Deliberately NOT adding ambiguous words that are also real English
# words (e.g. "ban") -- that would misroute genuine English sentences.
# Extend only with words confirmed in our own roster (see content.py).
_VN_BARE_WORDS = {"anh", "em", "ngon"}
_WORD_RE = re.compile(r"[a-zà-ỹđ]+", re.IGNORECASE)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _load_env() -> dict:
    with open(ENV_PATH, encoding="utf-8") as f:
        return dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))


def _is_vietnamese(text: str) -> bool:
    """Heuristic: Vietnamese-specific diacritics present, OR the whole text
    is just one of our known bare-ASCII Vietnamese words with nothing else
    around it (word-boundary match, so "em" doesn't fire inside "system" —
    and deliberately only for short standalone utterances, not embedded in
    a longer English sentence, to avoid misrouting real English text)."""
    if _VN_CHARS.search(text):
        return True
    words = _WORD_RE.findall(text.lower())
    return bool(words) and all(w in _VN_BARE_WORDS for w in words)


def split_by_voice(text: str) -> list[tuple[str, str]]:
    """Splits text into (voice_key, chunk) runs, voice_key in {"teacher","tutor"}.
    Splits on sentence boundaries -- a single sentence is never split mid-way."""
    sentences = _SENTENCE_SPLIT.split(text.strip())
    runs: list[tuple[str, str]] = []
    for s in sentences:
        if not s.strip():
            continue
        key = "teacher" if _is_vietnamese(s) else "tutor"
        if runs and runs[-1][0] == key:
            runs[-1] = (key, runs[-1][1] + " " + s)
        else:
            runs.append((key, s))
    return runs


def synthesize(text: str, voice_key: str) -> bytes:
    env = _load_env()
    name, gender, locale = TEACHER_VOICE if voice_key == "teacher" else TUTOR_VOICE
    ssml = (
        f"<speak version='1.0' xml:lang='{locale}'>"
        f"<voice xml:lang='{locale}' xml:gender='{gender}' name='{name}'>"
        f"{xml_escape(text)}"
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def speak(text: str) -> None:
    """Splits text by voice, synthesizes each run, plays them back in order."""
    for voice_key, chunk in split_by_voice(text):
        audio = synthesize(chunk, voice_key)
        tmp_path = Path(__file__).parent / "voices" / "_playback.wav"
        tmp_path.write_bytes(audio)
        winsound.PlaySound(str(tmp_path), winsound.SND_FILENAME)
