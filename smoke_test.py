"""Runs a whole session end to end with the network unplugged.

Exists because "import tutor" succeeding proves nothing: a signature that no
longer matches its call site only blows up when the line actually runs, and
that line is several minutes into a live lesson. This exercises the real
run_session -> _conversation_loop -> _run_turn -> _advance_lesson path with
the LLM, microphone and speech synthesis replaced by stubs, so wiring breaks
surface in a second instead of during a lesson.

Not a test of behaviour -- it asserts the machine turns over, nothing more.

Run: python smoke_test.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import tutor

SPOKEN: list[str] = []
instructions: list[str] = []


class FakeVoice:
    def say(self, text):
        SPOKEN.append(text)

    def wait(self):
        pass


def main() -> int:
    turns = {"n": 0}

    def fake_stream(api_key, models, messages, tools=None, rounds=5):
        """Records the single instruction the state machine hands over each turn,
        so the assertions below can check the plan really advances."""
        turns["n"] += 1
        instructions.append(messages[-1]["content"])
        yield ("content", "Ready to dive in?" if turns["n"] == 1 else "In Vietnamese, that's tôi.")
        yield ("tool_calls", [])

    def fake_listen():
        if turns["n"] >= 4:
            raise KeyboardInterrupt
        return "[lang:vi] tôi"

    tutor.stream_llm_reply = fake_stream
    tutor.listen_and_transcribe = fake_listen
    tutor.SpeechPipeline = lambda *a, **kw: FakeVoice()
    tutor.preload_model = lambda: None
    tutor.load_api_key = lambda: "fake-key"
    tutor.run_assessment = lambda *a, **kw: None
    tutor.ProgressStore.save = lambda self: None  # never touch real progress

    try:
        tutor.run_session()
    except KeyboardInterrupt:
        pass  # the intended way out
    except Exception as e:
        print(f"ECHEC — la session a plante : {type(e).__name__}: {e}")
        raise

    if not SPOKEN:
        print("ECHEC — la session n'a rien dit du tout")
        return 1
    steps = [n for n in instructions if "THIS TURN, THIS ONLY" in n]
    if not steps:
        print("ECHEC — aucune instruction d'etape n'a ete transmise au modele")
        return 1
    if len(set(steps)) < 2:
        print("ECHEC — la meme etape a ete servie deux fois : le plan n'avance pas")
        for n in steps:
            print("   ", n.splitlines()[-1][:100])
        return 1

    print(f"OK — session complete, {len(SPOKEN)} passages parles, {len(steps)} etapes distinctes servies")
    for n in steps:
        print("   ", n.splitlines()[-1][:110])
    return 0


if __name__ == "__main__":
    sys.exit(main())
