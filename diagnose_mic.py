"""Run this yourself: python diagnose_mic.py
Records a few seconds, reports whether real audio was captured, and
saves it to voices/_mic_test.wav so you can listen back to what your
mic actually picked up."""
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

from listen import record_until_silence, transcribe, SAMPLE_RATE

print("Parle des que tu vois le message d'ecoute, dis une phrase complete -- ca s'arrete tout seul.")
audio = record_until_silence()

print(f"\n--- Diagnostic ---")
print(f"Duree: {len(audio) / SAMPLE_RATE:.2f}s ({len(audio)} echantillons)")
if audio.size == 0:
    print("AUCUN echantillon capture -- le flux micro n'a rien enregistre du tout.")
else:
    max_amp = int(np.abs(audio).max())
    rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
    print(f"Amplitude max: {max_amp} / 32767")
    print(f"RMS (niveau moyen): {rms:.1f}")
    if max_amp < 100:
        print(">>> QUASI SILENCE capte -- le micro n'entend rien (mauvais peripherique ou permissions Windows).")
    else:
        print(">>> Un vrai signal audio a ete capte.")

    out_path = "voices/_mic_test.wav"
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio.tobytes())
    print(f"Sauvegarde dans {out_path} -- tu peux l'ecouter pour verifier.")

    print("\nTranscription Whisper de ce que tu as dit :")
    text, lang = transcribe(audio)
    print(f"  [{lang}] {text!r}")
