import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/mathi/dev/viet-tutor/.env", encoding="utf-8") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line)

KEY = env["AZURE_SPEECH_KEY"]
REGION = env["AZURE_SPEECH_REGION"]

req = urllib.request.Request(
    f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list",
    headers={"Ocp-Apim-Subscription-Key": KEY},
)
with urllib.request.urlopen(req, timeout=30) as resp:
    voices = json.loads(resp.read().decode("utf-8"))

vi_voices = [v for v in voices if v["Locale"].startswith("vi")]
print(f"{len(vi_voices)} voix vietnamiennes trouvees:\n")
for v in vi_voices:
    styles = v.get("StyleList", [])
    print(f"- {v['ShortName']} ({v['Gender']}) — {v.get('LocalName', v['DisplayName'])}"
          + (f" [styles: {styles}]" if styles else ""))
