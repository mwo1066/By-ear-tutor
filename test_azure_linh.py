import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/mathi/dev/viet-tutor/.env", encoding="utf-8") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line)

KEY = env["AZURE_SPEECH_KEY"]
REGION = env["AZURE_SPEECH_REGION"]

TEXT = "Chào bạn! Bạn khỏe không? Tôi tên là Nam. Bạn có muốn ăn cơm không? Cà phê cũng ngon lắm!"
VOICE = "vi-VN-Linh:MAI-Voice-2-Flash"

ssml = f"""<speak version='1.0' xml:lang='vi-VN'>
  <voice xml:lang='vi-VN' xml:gender='Female' name='{VOICE}'>
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
    out_path = "C:/Users/mathi/dev/viet-tutor/voices/test_azure_linh_flash.wav"
    with open(out_path, "wb") as f:
        f.write(audio)
    print(f"OK -> {out_path} ({len(audio)} bytes)")
except urllib.error.HTTPError as e:
    print(f"ERREUR: {e.code} {e.read().decode('utf-8', errors='replace')}")
