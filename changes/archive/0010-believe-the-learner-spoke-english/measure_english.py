"""The learner asking for help in English is a designed path -- rules 4b-bis,
4c, 4c-bis. This measures whether the two forced readings can tell it apart
from a Vietnamese attempt WITHOUT asking Whisper to guess the language.

For each thing said: decode forced vi, decode forced en, and print both with
their word counts. What we are looking for is whether the ENGLISH reading is
long and clean when English was spoken, and short nonsense when a Vietnamese
word was spoken. If it is, that is the discriminator and no language guess is
needed anywhere.
"""
import json, sys, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import listen

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def ask(wav_bytes, language):
    boundary = uuid.uuid4().hex
    fields = {"model": listen.STT_MODEL, "response_format": "verbose_json", "temperature": "0"}
    if language:
        fields["language"] = language
    parts = [f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8")
             for k, v in fields.items()]
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\n"
        f"Content-Type: audio/wav\r\n\r\n".encode("utf-8") + wav_bytes + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
        headers={"Authorization": f"Bearer {listen._load_groq_key()}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}",
                 "User-Agent": UA}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


# EN  -- asking for help, the shortest form of free speech
# ASK -- stopping the lesson to steer it. These carry an INSTRUCTION, so the
#        English text has to survive intact, not merely be recognised as English.
# VI  -- the control group: real attempts at a word.
SAY = [
    ("EN", "Can you repeat that?"),
    ("EN", "I didn't understand"),
    ("EN", "I forgot"),
    ("ASK", "Can we work on numbers now?"),
    ("ASK", "I want to practise asking questions instead"),
    ("VI", "toi"),
    ("VI", "khong"),
]

rows = []
for kind, phrase in SAY:
    input(f'\n  [{kind}] say:  "{phrase}"   -- press Enter, then say it: ')
    audio = listen.record_until_silence()
    if audio.size == 0:
        print("    nothing captured, skipping")
        continue
    wav = listen._audio_to_wav_bytes(audio)
    auto = ask(wav, None)
    vi = ask(wav, "vi").get("text", "").strip()
    en = ask(wav, "en").get("text", "").strip()
    rows.append((kind, phrase, auto.get("language"), vi, en))
    print(f"    auto guessed : {auto.get('language')}  ->  {auto.get('text','').strip()!r}")
    print(f"    forced vi    : {vi!r}   ({len(vi.split())} words)")
    print(f"    forced en    : {en!r}   ({len(en.split())} words)")

print("\n" + "=" * 78)
print(f"{'':4} {'said':<24} {'guess':<11} {'en words':<9} {'forced en'}")
for kind, phrase, guess, vi, en in rows:
    print(f"{kind:<4} {phrase:<24} {str(guess):<11} {len(en.split()):<9} {en!r}")
print("\nThe question: is there a word count that separates the EN rows from the VI rows?")
