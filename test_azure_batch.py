import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/mathi/dev/viet-tutor/.env", encoding="utf-8") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line)

KEY = env["AZURE_SPEECH_KEY"]
REGION = env["AZURE_SPEECH_REGION"]

TEXT = "Nice! You got that one right. Okay, let's try the next word -- listen carefully, this one's a bit trickier."

VOICES = [
    ("en-US-AriaNeural", "Female", "en-US"),
    ("en-US-SaraNeural", "Female", "en-US"),
    ("en-US-NancyNeural", "Female", "en-US"),
    ("en-US-JaneNeural", "Female", "en-US"),
    ("en-US-AmandaMultilingualNeural", "Female", "en-US"),
    ("en-US-PhoebeMultilingualNeural", "Female", "en-US"),
    ("en-US-GuyNeural", "Male", "en-US"),
    ("en-US-DavisMultilingualNeural", "Male", "en-US"),
    ("en-US-ChristopherMultilingualNeural", "Male", "en-US"),
    ("en-US-RyanMultilingualNeural", "Male", "en-US"),
    ("en-US-AlloyTurboMultilingualNeural", "Male", "en-US"),
    ("en-GB-SoniaNeural", "Female", "en-GB"),
]

for voice, gender, locale in VOICES:
    ssml = f"""<speak version='1.0' xml:lang='{locale}'>
      <voice xml:lang='{locale}' xml:gender='{gender}' name='{voice}'>
        {TEXT}
      </voice>
    </speak>"""
    req = urllib.request.Request(
        f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "viet-tutor-test",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            audio = resp.read()
        out_path = f"C:/Users/mathi/dev/viet-tutor/voices/batch_{voice}.wav"
        with open(out_path, "wb") as f:
            f.write(audio)
        print(f"OK: {voice}")
    except urllib.error.HTTPError as e:
        print(f"ERREUR {voice}: {e.code} {e.read().decode('utf-8', errors='replace')}")
