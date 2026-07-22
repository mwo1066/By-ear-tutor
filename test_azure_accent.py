import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/mathi/dev/viet-tutor/.env", encoding="utf-8") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line)

KEY = env["AZURE_SPEECH_KEY"]
REGION = env["AZURE_SPEECH_REGION"]

TEXT = "Nice! You got that one right. Okay, let's try the next word -- listen carefully, this one's a bit trickier."

# Feed English text to the Vietnamese female voice -- testing if it carries
# a Vietnamese accent, since the model never learned true English phonemes.
ssml = f"""<speak version='1.0' xml:lang='vi-VN'>
  <voice xml:lang='vi-VN' xml:gender='Female' name='vi-VN-HoaiMyNeural'>
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
    out_path = "C:/Users/mathi/dev/viet-tutor/voices/test_hoaimy_english_accent.wav"
    with open(out_path, "wb") as f:
        f.write(audio)
    print(f"OK -> {out_path} ({len(audio)} bytes)")
except urllib.error.HTTPError as e:
    print(f"ERREUR: {e.code} {e.read().decode('utf-8', errors='replace')}")
