"""One recording, decoded three ways. Does telling Whisper the language fix it?

Pass 1 in the tutor runs with no language at all -- Whisper guesses from a
one-second clip. This asks whether that guess is what breaks, by decoding the
exact same audio with the guess, with Vietnamese forced, and with English forced.
"""
import json, urllib.request, uuid
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


WORDS = ["tôi", "tên", "là", "không", "chào"]
print("Five words, one at a time. Say each one when asked.\n")
results = []
for word in WORDS:
    input(f"  ready for  {word}  -- press Enter, then say it: ")
    audio = listen.record_until_silence()
    if audio.size == 0:
        print("    nothing captured, skipping\n")
        continue
    wav = listen._audio_to_wav_bytes(audio)
    row = {"said": word}
    for label, lang in (("guessed", None), ("forced vi", "vi"), ("forced en", "en")):
        p = ask(wav, lang)
        row[label] = f"{p.get('text','').strip()!r}"
        if lang is None:
            row["guess"] = p.get("language")
    results.append(row)
    print(f"    guessed {row['guess']:<12} {row['guessed']}")
    print(f"    forced vi                {row['forced vi']}")
    print(f"    forced en                {row['forced en']}\n")

print("\n" + "=" * 64)
print(f"{'said':<8} {'guess':<11} {'auto':<20} {'forced vi':<20} {'forced en'}")
for r in results:
    print(f"{r['said']:<8} {str(r['guess']):<11} {r['guessed']:<20} {r['forced vi']:<20} {r['forced en']}")
