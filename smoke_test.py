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
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import content
import listen
import srs
import tutor
import voice

SPOKEN: list[str] = []
instructions: list[str] = []
expectations: list = []
scripted: list[tuple[str, str, bool]] = []  # (target, line, is_retry) per turn the code wrote itself


class FakeVoice:
    def say(self, text):
        SPOKEN.append(text)

    def wait(self):
        pass


# Lines the tutor really said in a live session, each one heard wrong at the
# time, kept so that the fix stays fixed. This is the point of writing them
# down: a fix verified by "run a lesson and listen" is a fix that can quietly
# stop applying -- which already happened once here, to a vad_filter fix left
# on a code path nothing called.
#
# Add a case when a lesson goes wrong, not a rule. If a new failure needs a new
# entry in a list somewhere to pass, the list is the problem, not the entry.
VOICE_CASES = [
    # 2026-08-10 -- no space around the dash, so "correct—là." was one token and
    # the whole thing went to the English voice. Minh never said "là".
    ("That's correct—là.", [("tutor", "That's correct—"), ("teacher", "là.")]),
    # The same sentence spaced normally always worked; it must keep working.
    ("In Vietnamese, that's tôi.", [("tutor", "In Vietnamese, that's"), ("teacher", "tôi.")]),
    # A scripted turn: the target belongs to Minh, the question to the tutor.
    ("Listen again — tôi. And again?",
     [("tutor", "Listen again —"), ("teacher", "tôi."), ("tutor", "And again?")]),
    # An introduction: the meaning is the tutor's, both sayings of the word are
    # Minh's, and they merge into one clip so he says it twice in a breath.
    ("In Vietnamese, the word for name is tên. tên. Now you say it.",
     [("tutor", "In Vietnamese, the word for name is"), ("teacher", "tên. tên."),
      ("tutor", "Now you say it.")]),
    # 2026-08-11 -- a frequency import put bare-ASCII Vietnamese words into the
    # routing vocabulary, and several of them are English words. Minh started
    # pronouncing "So" and "Do" inside the tutor's own English sentences.
    ("So how would you say it?", [("tutor", "So how would you say it?")]),
    ("Do you want a coffee?", [("tutor", "Do you want a coffee?")]),
    # 2026-08-11 -- a proper name has no diacritics, so it fell back to the
    # English voice in the middle of Minh's own sentence: "Em tên là" then
    # "Nam." in a woman's English accent.
    ("The natural way is Em tên là Nam.",
     [("tutor", "The natural way is"), ("teacher", "Em tên là Nam.")]),
    ("Tôi tên là Nam.", [("teacher", "Tôi tên là Nam.")]),
    # …and the same shape must NOT swallow the next sentence's first word.
    ("In Vietnamese, the word for name is tên. Now you say it.",
     [("tutor", "In Vietnamese, the word for name is"), ("teacher", "tên."),
      ("tutor", "Now you say it.")]),
    # Digits are nobody's vocabulary but must still be spoken.
    ("I have 1975 words.", [("tutor", "I have 1975 words.")]),
    # 2026-08-13 -- the model answered in markdown. The stream split
    # "**Tôi cũng muốn ăn.**" and a bare "**" arrived as its own line, was
    # routed to the tutor voice and sent to Azure, which returned an empty
    # clip. Routing must see the same text synthesis will.
    ("**Tôi cũng muốn ăn.**", [("teacher", "Tôi cũng muốn ăn.")]),
    ("The full sentence is: **Tôi cũng muốn ăn.**",
     [("tutor", "The full sentence is:"), ("teacher", "Tôi cũng muốn ăn.")]),
]

# 2026-08-10 -- the model cued Minh with a bare "Minh.", which the colon-only
# label regex missed, so the English voice announced it out loud. The other
# forms have not been seen yet and are here to prove the rule does not care.
STAGE_DIRECTIONS = ["Minh.", "Minh", "(Minh)", "Minh --", "  minh  "]
NOT_STAGE_DIRECTIONS = ["Minh says hello.", "Minh: tôi.", "tôi."]


# (target, what was said, should the guard fire). The construction cases are
# the point: the guard could not fire on one at all until the placeholder was
# taken out of the comparison, so "Tôi tên là Nam." said on a step that forbids
# it went unreported through every session logged.
LEAK_CASES = [
    ("tôi tên là + [tên riêng]", "Tôi tên là Nam.", True),
    ("tôi tên là + [tên riêng]", "So how would you say My name is, with a name?", False),
    ("tôi tên là + [tên riêng]", "Minh: tôi là. How would you say I am ___?", False),
    ("Tôi ... tuổi", "Tôi hai mươi tuổi.", True),
    ("tôi", "In Vietnamese that is tôi.", True),
    ("tôi", "And again — what was I or me?", False),
]


# A construction is STORED as "muốn + [động từ]" and SAID as "muốn". Every line
# that names a target aloud has to use the spoken form -- the retry and the
# acknowledgement both did it wrong, one after the other, and Minh recited the
# placeholder as if it were words.
SPOKEN_TARGETS = [
    ("muốn + [động từ]", "muốn"),
    ("tôi tên là + [tên riêng]", "tôi tên là"),
    ("Tôi ... tuổi", "Tôi tuổi"),
    ("thích", "thích"),
]


def check_spoken_targets() -> int:
    failed = 0
    for stored, spoken in SPOKEN_TARGETS:
        got = " ".join(tutor._target_fragments(stored))
        if got != spoken:
            print(f"FAIL — {stored!r} would be said as {got!r}, expected {spoken!r}")
            failed += 1
    return failed


def check_leak_cases() -> int:
    """A turn that forbids saying the answer, and says it, must be reported."""
    failed = 0
    for target, said, expected in LEAK_CASES:
        step = tutor.Step("vary", target, "", answer_is_target=True)
        if tutor._leaked_target(said, step) != expected:
            verb = "missed" if expected else "wrongly flagged"
            print(f"FAIL — leak guard {verb} {said!r} against target {target!r}")
            failed += 1
    return failed


# An API refusal either gets retried or does not, and getting that wrong is
# expensive in both directions. Live: a 400 (truncated tool-call JSON) was
# retried five times, burning budget on a request that could never succeed, and
# then crashed the lesson.
ERROR_CASES = [
    ({"status_code": 400, "code": "tool_use_failed"}, True),   # our request is wrong
    ({"status_code": 422}, True),
    ({"status_code": 429}, False),                             # slow down, then it works
    ({"status_code": 503}, False),
    ({"message": "connection reset"}, False),                  # no status: assume transient
]


# (what pass 1 heard, the language it reported, the word the step was waiting
# for, is this the learner talking).
# The first line is the one that mattered: it was overwritten by a forced
# Vietnamese second pass, scored as a correct answer, and the lesson carried on.
TALKING_CASES = [
    ("No, I'm asking for travel, listen, I don't care what I am me.", "en", "tôi", True),
    ("Can we do a lesson about ordering food?", "en", "tôi", True),
    ("toi", "en", "tôi", False),          # an attempt, badly spelled
    ("Fen Bey.", "en", "sân bay", False), # an attempt at sân bay
    ("and Bay", "en", "sân bay", False),
    # 2026-08-17 -- said aloud into the microphone. All three are shorter than
    # the four words the guard used to demand, so the forced pass ran and
    # TRANSLATED them: "I didn't understand" came back "Tôi không hiểu.", which
    # contains both tôi and không and scored a correct answer. The learner says
    # they did not understand and is told "Exactly."
    ("I forgot.", "en", "không", True),
    ("I don't understand.", "en", "không", True),
    ("You repeat that.", "en", "tôi", True),
    ("We work on number nine.", "en", "không", True),
    # …and a badly heard one-word attempt must STILL reach the forced pass, even
    # resembling nothing at all: "Bye!" against tôi scores 0.000. This is why
    # English counts as speech from two words, not one.
    ("Bye!", "en", "tôi", False),
    ("Huh.", "en", "không", False),
    ("Tôi tên là Nam", "vi", "tôi", False),  # Vietnamese: never treated as talking
    # 2026-08-13 -- the learner asked out loud for the answer to be given to
    # them. Pass 1 decoded it as KOREAN, so a guard testing lang == "en" never
    # fired, and a forced-Vietnamese pass invented "Tôi... Chị... Giờ giải
    # thích cho tôi" which reached the lesson behind a [lang:vi] tag. Only the
    # language and the length were recorded, not pass 1's own text.
    ("neun jeoneun seonsaengnim kke jilmun", "ko", "tôi", True),
    ("Tôi cũng muốn ăn", "vi", "ăn", False),  # …and a long real attempt still is not talking
]


# (what was heard, the target, should it count). Every one of these came out of
# a real session. A recogniser feeding a beginner through a noisy microphone is
# the normal case, so the bar is generous on purpose -- but not so generous that
# a single letter, or one shared letter out of two, records a word as known.
ANSWER_CASES = [
    # 2026-08-13 -- room noise, and Whisper answered with YouTube boilerplate it
    # was trained on. "ăn" bare is "an", which sits inside "dẫn", so with word
    # boundaries dropped the hallucination counted as the answer and the word
    # was recorded as known.
    ("[lang:vi] Hãy subscribe cho kênh Ghiền Mì Gõ Để không bỏ lỡ những video hấp dẫn", "ăn", False),
    ("[lang:vi] Tôi muốn ăn.", "ăn", True),      # …and a real one still counts
    ("[lang:vi] G", "chị", False),               # a single letter never was an answer
    ("Dạ", "là", False),        # one shared letter out of two: was accepted, level went to 7
    ("D", "đi", False),         # a single letter is not a word
    ("Đôi", "tôi", True),       # two of three: a real recognition
    ("toi", "tôi", True),
    ("Thôi", "tôi", True),
    ("Chí", "chị", True),
    ("moon", "muốn", True),
    ("Tết", "thích", False),
]


def check_answer_cases() -> int:
    failed = 0
    for said, target, expected in ANSWER_CASES:
        if tutor.answered_target(f"[lang:vi] {said}", target) != expected:
            verb = "counted" if expected else "refused"
            print(f"FAIL — {said!r} against {target!r} should be {verb}")
            failed += 1
    return failed


# Two real turns, replayed end to end with the network replaced by what Groq
# actually returned. Both were failures on 17 August, and neither is visible at
# the level of is_learner_talking alone -- they are decided by the whole chain.
# (title, expected word, {forced language: what Groq returned}, wanted outcome)
TRANSCRIBE_CASES = [
    ("'too fast' said aloud on a step asking for tôi", "tôi",
     {None: ("Tu fast", "it"), "vi": ("TÙ PHÁST", "vi"), "en": ("too fast", "en")},
     ("too fast", "en")),
    # Pass 1 called it Korean, so length decided: four words, therefore "a
    # sentence", therefore decoded as English -> "Totten-Lay-Anna.", handed over
    # as a question, and the tutor answered with the sentence the learner had
    # just produced correctly.
    ("'Tôi tên là Anna' said correctly, tagged Korean", "tôi tên là + [tên riêng]",
     {None: ("neun jeoneun", "ko"), "en": ("Totten-Lay-Anna.", "en"),
      "vi": ("Tôi tên là Anna", "vi")},
     ("Tôi tên là Anna", "vi")),
]


def check_transcribe_cases() -> int:
    import numpy as np
    failed = 0
    real = listen._run_transcribe_groq
    try:
        for title, expected, script, want in TRANSCRIBE_CASES:
            listen._run_transcribe_groq = lambda wav, language, prompt, s=script: s[language]
            got = listen.transcribe(np.ones(16000, dtype=np.int16), expected=expected,
                                    matches=tutor.answered_target,
                                    resembles=tutor.resembles_target)
            if got != want:
                print(f"FAIL — {title}: got {got}, wanted {want}")
                failed += 1
    finally:
        listen._run_transcribe_groq = real
    return failed


def check_talking_cases() -> int:
    failed = 0
    for text, lang, target, expected in TALKING_CASES:
        if listen.is_learner_talking(text, lang, target, tutor.resembles_target) != expected:
            verb = "kept as heard" if expected else "left to the second pass"
            print(f"FAIL — {text!r} ({lang}) should be {verb}")
            failed += 1
    return failed


def check_derived_pieces(roster) -> int:
    """The code must read off a sentence's pieces exactly as a human wrote them.

    No hardcoded expectations here on purpose: the hand-written constructions
    ARE the corpus, so this cannot drift away from the content the way a copied
    list would. It is also the whole argument for computing the field instead
    of asking the model -- which got 8 of its 13 wrong on the same test.

    Each construction is derived against the items declared BEFORE it, never the
    whole roster, because that is all the live loop ever has: a piece is a
    prerequisite, and a word introduced later in the course cannot be one. The
    whole roster made a homograph look like a defect -- "phải" the modal, added
    far later, sits inside the early "không phải là" without being the same word
    in any sense the learner needs.
    """
    failed = 0
    for n, item in enumerate(roster):
        if item.kind != "construction" or not item.pieces:
            continue
        got = content.derive_pieces(item.name, roster[:n])
        if got != item.pieces:
            print(f"FAIL — pieces of {item.name!r}\n      hand-written {item.pieces}\n      derived      {got}")
            failed += 1
    return failed


def check_error_cases() -> int:
    failed = 0
    for error, permanent in ERROR_CASES:
        if tutor._permanent(error) != permanent:
            expected = "never retried" if permanent else "retried"
            print(f"FAIL — {error} should be {expected}")
            failed += 1
    return failed


def check_voice_cases(vocab) -> int:
    """Replays the recorded failures. Returns the number that still fail."""
    failed = 0
    for text, expected in VOICE_CASES:
        got = voice.split_by_voice(text, vocab)
        if got != expected:
            print(f"FAIL — voice routing for {text!r}\n      expected {expected}\n      got      {got}")
            failed += 1
    for text in STAGE_DIRECTIONS:
        if not voice.is_stage_direction(text):
            print(f"FAIL — {text!r} is a stage direction and would be spoken aloud")
            failed += 1
    for text in NOT_STAGE_DIRECTIONS:
        if voice.is_stage_direction(text):
            print(f"FAIL — {text!r} is real speech and would be dropped")
            failed += 1
    return failed


def check_every_plan_builds() -> int:
    """build_plan must survive every item the course can reach, in real order.

    The session test below runs eight turns and stops, so it only ever plans
    the first two or three items -- all atoms. Constructions and rules come
    much later, and one of them had been raising UnboundLocalError for three
    commits: a duplicated `elif item.kind == "construction"` left the OLD
    branch in place as dead code, while the live one lost its short closing
    step to a pasted copy of the rule branch's, which reads a variable that
    only exists there.

    Nothing caught it because nothing had ever planned a construction. Every
    item, in the order the sequencing produces, is the only bar that means
    anything here.
    """
    random.seed(7)
    queue = [i for i in content.load_course(tutor.CONTENT_DIR) if content.is_teachable(i)]
    store = srs.ProgressStore(None)
    seen: list = []
    failed = 0
    while queue:
        item = queue.pop(content.pick_next_index(queue, seen))
        seen.append(item)
        store.mark_introduced(item.name)
        pieces = content.pieces_of(item, seen)
        try:
            plan = tutor.build_plan(item, pieces,
                                    tutor._recall_targets(store, item, pieces, seen), seen)
        except Exception as exc:
            print(f"FAIL — planning {item.kind} {item.name!r} raised {type(exc).__name__}: {exc}")
            failed += 1
            continue
        if not plan:
            print(f"FAIL — {item.kind} {item.name!r} produced an empty plan")
            failed += 1
        for step in plan:
            if step.kind in tutor.SCORING_KINDS and step.target:
                store.record_recall(step.target)
    return failed



# (line, is the Vietnamese stranded mid-sentence). Counting per LINE accused the
# course's own introduce turn, which switches voice twice and is exactly right:
# the Vietnamese ends its sentence and a new one follows. The defect is a switch
# INSIDE a sentence, where a second voice says a word and the first resumes.
CHOPPY_CASES = [
    ("In Vietnamese, the word for name is tên. tên. Now you say it.", False),
    ("In Vietnamese, that's tôi.", False),
    ("Listen again — tôi. And again?", False),
    ("Three little words—đã, đang, sẽ—show past, present and future.", True),
    # The tone-twin introduction: four Vietnamese words across the line, every
    # run ending its own sentence, and the ask last. The first version bolted
    # the contrast onto the ordinary template and left "Now you say it" in the
    # middle, so the learner was told to speak and then talked over.
    ("In Vietnamese, the word for one, as in twenty-one is mốt. mốt. Careful — you already "
     "know one, and it is the same sounds at a different pitch. Here they are together: "
     "một. mốt. Now you say it.", False),
    # Three examples in a row, but the Vietnamese still ENDS the sentence, so
    # this is not the defect -- it is a separate question of how much to say
    # at once, and flagging it here would blunt the signal.
    ("They go right before the verb, like “Tôi đã ăn,” “Tôi đang ăn,” “Tôi sẽ ăn.”", False),
    # The line from the same turn that IS the defect: a pattern named in the
    # middle, the tutor resuming after it.
    ("You’ve already used the pattern “tôi tên là …,” so you can try it with a tense marker.", True),
]


def check_choppy_cases(vocab) -> int:
    """A line the tutor really said, and whether it strands Vietnamese."""
    import io
    import contextlib
    failed = 0
    for text, expected in CHOPPY_CASES:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            voice._warn_if_choppy(text, vocab)
        got = bool(buf.getvalue().strip())
        if got != expected:
            verb = "missed" if expected else "wrongly flagged"
            print(f"FAIL — choppiness guard {verb} {text[:52]!r}")
            failed += 1
    return failed


# (line, kind of turn, does it state its own answer). A rule or an application
# asks for a whole sentence, so _leaked_target -- which needs a known target
# word -- could never fire on one. Every line here was really said by the tutor
# while the tier-1 rules were being rendered one by one.
ANSWER_ALOUD_CASES = [
    ("How would you say “anh ấy”?", "apply", True),
    # Said by a rule turn when rule turns still asked. Kept as an apply case:
    # a rule turn only TELLS now, so naming Vietnamese in one is legitimate,
    # and the same line on the turn that asks is still the defect.
    ("How would you say “bạn ơi, tên là gì?” to Minh?", "apply", True),
    ("How would you say “I don’t want to eat” using the pattern “không muốn + [động từ]”?",
     "apply", True),
    # Naming the material one word at a time is a fair question, not a leak.
    ("So how would you say “he” using anh and ấy?", "apply", False),
    ("How would you call a male friend using “anh” and “ơi”?", "apply", False),
    ("How would you say “not want” in Vietnamese?", "apply", False),
    # An introduction SAYS the word on purpose; it is not an asking turn.
    ("In Vietnamese, the word for name is tên. tên. Now you say it.", "introduce", False),
]


def check_answer_aloud_cases(roster) -> int:
    import contextlib
    import io
    failed = 0
    for text, kind, expected in ANSWER_ALOUD_CASES:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tutor._warn_if_answer_spoken(text, tutor.Step(kind, "x", ""), roster)
        if bool(buf.getvalue().strip()) != expected:
            verb = "missed" if expected else "wrongly flagged"
            print(f"FAIL — answer-aloud guard {verb} {text[:56]!r}")
            failed += 1
    return failed



# (line, what should survive to the speakers). A line that is ONLY a name is
# dropped by is_stage_direction; these are the other half -- a cue in FRONT of
# real speech, where the tutor's own voice read the label out loud. Heard live:
# "Minh says: cho." The colon is what separates a cue from a real line.
SPEAKER_CUE_CASES = [
    ("Minh says: cho.", "cho."),
    ("Minh: tôi.", "tôi."),
    ("minh repeats: ăn", "ăn"),
    # Both of these are real speech and must survive untouched.
    ("Minh says hello.", "Minh says hello."),
    ("Minh, say hello to our new student.", "Minh, say hello to our new student."),
    ("I said no.", "I said no."),
]


def check_speaker_cues() -> int:
    import contextlib
    import io
    failed = 0
    for text, expected in SPEAKER_CUE_CASES:
        with contextlib.redirect_stdout(io.StringIO()):
            got = voice._strip_authoring_notation(text)
        if got != expected:
            print(f"FAIL — {text!r} became {got!r}, expected {expected!r}")
            failed += 1
    return failed



def check_feature_glosses_name_their_word(roster) -> int:
    """A rule ABOUT a word must NAME that word in its gloss.

    The gloss is what the model is told to say, so a gloss reading "to say
    something will happen, one word goes before the action" leaves it to guess
    WHICH word -- and guessing is where every invented sentence tonight came
    from. Measured before fixing: 25 of 35 glosses contained no Vietnamese at
    all.

    Only rules whose subject IS a word are checked. "verbs never change" and
    "no genders, no articles" are about an ABSENCE and have nothing to name;
    the test for that is whether the rule's own pieces include a function word
    it is built on.
    """
    failed = 0
    for item in roster:
        if item.kind != "feature" or not item.gloss:
            continue
        subject = next((p for p in item.pieces if p in item.name), None)
        if subject and subject not in item.gloss:
            print(f"FAIL — rule {item.name!r} is about {subject!r} and never names it: "
                  f"{item.gloss!r}")
            failed += 1
    return failed



def check_glosses_cite_only_taught_words(roster) -> int:
    """A rule's gloss may only quote Vietnamese the course actually teaches.

    The gloss is recited aloud, so a word quoted in it is a word the learner is
    expected to recognise. Sibling to the mistake that produced this check from
    the other side: the adjective rule was given "a name, a job, a nationality"
    as its illustrations, and the course can say none of job or nationality --
    so the model filled the gap with "tên tôi", which is possession and has
    nothing to do with the rule.

    Syllable-aware: "cà phê" is one taught item and must not be read as two
    unknown words.
    """
    syllables = {s.lower() for i in roster if content.is_teachable(i)
                 for s in i.name.split()}
    failed = 0
    for item in roster:
        if item.kind != "feature" or not item.gloss:
            continue
        for raw in item.gloss.replace(",", " ").replace(":", " ").replace("—", " ").split():
            word = raw.strip("\"'.?!()").lower()
            if not word or not any(ord(c) > 127 for c in word):
                continue
            if word not in syllables:
                print(f"FAIL — rule {item.name!r} quotes {word!r}, which the course never teaches")
                failed += 1
    return failed


def check_pieces_exist(roster) -> int:
    """Every declared piece must be a teachable item.

    A piece that does not exist is not a typo, it is a rule that can never be
    taught: unknown_pieces never empties, so the sequencing holds it back for
    ever and nothing says so. Written after declaring "nhà" as a piece of the
    location rule -- a word the course does not contain.
    """
    names = {i.name for i in roster if content.is_teachable(i)}
    failed = 0
    for item in roster:
        for piece in item.pieces:
            if piece not in names:
                print(f"FAIL — {item.name!r} declares piece {piece!r}, which is not a teachable item")
                failed += 1
    return failed


def check_prerequisite_order() -> int:
    """Nothing may be taught before the words it is made of -- run over the
    WHOLE course, not a sample.

    This is the one guarantee the sequencing exists to provide, and the only
    one the prompt could never make on its own. It broke silently: "đi" existed
    both in the roster and in the personal items, so a rule's prerequisite was
    satisfied by the personal copy while the roster copy was still queued, and
    the composition rule came out at 152 with its own piece not due until 182.
    Nothing failed, nothing printed -- the lesson would simply have taught a
    rule about a word the learner had never heard.

    Replays the real sequencing to the end rather than checking the declared
    fields, because the fields were all correct; it was the ORDER they produced
    that was wrong.
    """
    random.seed(7)
    queue = [i for i in content.load_course(tutor.CONTENT_DIR) if content.is_teachable(i)]
    seen: list = []
    order = []
    while queue:
        item = queue.pop(content.pick_next_index(queue, seen))
        seen.append(item)
        order.append(item)
    at = {i.name: n for n, i in enumerate(order)}
    failed = 0
    for n, item in enumerate(order):
        late = [p for p in item.pieces if at.get(p, -1) > n]
        if late:
            print(f"FAIL — {item.name!r} is taught at {n} but needs "
                  + ", ".join(f"{p!r} (taught at {at[p]})" for p in late))
            failed += 1
    return failed


def main(NO_INTRO=False) -> int:
    # Offline and instant, so it runs first: no point exercising the lesson
    # loop if the voices are wrong about who says what.
    roster = content.load_roster(tutor.CONTENT_DIR)
    vocab = tutor._vocab_words(roster)
    if (check_voice_cases(vocab) + check_leak_cases() + check_error_cases()
            + check_talking_cases() + check_transcribe_cases()
            + check_derived_pieces(roster)
            + check_spoken_targets() + check_answer_cases()
            + check_prerequisite_order()
            + check_every_plan_builds() + check_choppy_cases(vocab) + check_answer_aloud_cases(roster) + check_pieces_exist(roster) + check_speaker_cues() + check_feature_glosses_name_their_word(roster)
            + check_glosses_cite_only_taught_words(roster)):
        return 1

    turns = {"n": 0}

    def fake_stream(api_key, models, messages, tools=None, rounds=5, max_tokens=None):
        """Records the single instruction the state machine hands over each turn,
        so the assertions below can check the plan really advances."""
        turns["n"] += 1
        instructions.append(messages[-1]["content"])
        yield ("content", "Ready to dive in?" if turns["n"] == 1 else "In Vietnamese, that's tôi.")
        yield ("tool_calls", [])

    def fake_listen(expected=None, matches=None, resembles=None):
        # Signature mirrors the real one on purpose: this test exists to catch
        # exactly the kind of mismatch that only shows up mid-lesson otherwise.
        expectations.append(expected)
        # Counted in turns SPOKEN, not requests made: most of a lesson is
        # scripted now and never reaches fake_stream, so counting requests
        # would run the session on for ever.
        if len(SPOKEN) >= 8:
            raise KeyboardInterrupt
        return "[lang:vi] tôi"

    real_scripted_turn = tutor.scripted_turn

    def watched_scripted_turn(lesson):
        """Records what the code chose to say for itself, and for which word --
        the two halves the assertions below need to prove a scripted question
        never contains its own answer."""
        line = real_scripted_turn(lesson)
        if line is not None:
            step = tutor.current_step(lesson)
            # Two turns say the target on purpose: an introduction (the word IS
            # the news) and a retry (Minh gives it before asking again).
            by_design = bool(lesson.get("retried")) or step.kind == "introduce"
            scripted.append((step.target, line, by_design))
        return line

    tutor.scripted_turn = watched_scripted_turn
    tutor.stream_llm_reply = fake_stream
    tutor.listen_and_transcribe = fake_listen
    tutor.SpeechPipeline = lambda *a, **kw: FakeVoice()
    tutor.preload_model = lambda: None
    tutor.load_api_key = lambda: "fake-key"
    tutor.run_assessment = lambda *a, **kw: None
    tutor.ProgressStore.save = lambda self: None  # never touch real progress

    try:
        tutor.run_session(no_intro=NO_INTRO)
    except KeyboardInterrupt:
        pass  # the intended way out
    except Exception as e:
        print(f"FAIL — the session crashed: {type(e).__name__}: {e}")
        raise

    if not SPOKEN:
        print("FAIL — the session said nothing at all")
        return 1
    # The opening turn must ask for the opening speech, not the wind-down.
    # An empty plan means both "not started" and "finished", and conflating
    # them once made the tutor greet with "let's wrap up for today".
    if not NO_INTRO and "OPENING SPEECH" not in instructions[0]:
        print("FAIL — the first turn did not ask for the opening speech:")
        print("   ", instructions[0].splitlines()[-1][:120])
        return 1

    # No longer required to be non-empty: a run of simple words is fully
    # scripted now, so a short session can legitimately serve the model nothing
    # but the opening. What must hold is that WORK was served -- see `served`.
    steps = [n for n in instructions if "THIS TURN, THIS ONLY" in n]

    # The mechanical turns are the point of the state machine: if none fired,
    # the model is back to running the whole cycle and the drift comes with it.
    if not scripted:
        print("FAIL — no turn was written by the code; every one went to the model")
        return 1
    # A scripted recall is built from the gloss alone precisely so that it
    # cannot state its own answer. This is the assertion that keeps it true.
    # The introduction and the retry are the exceptions, and they declare it.
    for target, line, by_design in scripted:
        if by_design or not target:
            continue
        if target.casefold() in line.casefold():
            print(f"FAIL — a scripted turn asking for {target!r} said it: {line!r}")
            return 1
    lines = [line for _, line, _ in scripted]
    if len(lines) > 1 and len(set(lines)) == 1:
        print(f"FAIL — every scripted turn used the same wording: {lines[0]!r}")
        return 1

    # Distinct WORK done, from either mouth: the plan has to move.
    served = set(steps) | set(lines)
    if len(served) < 2:
        print("FAIL — the same turn was served twice: the plan is not advancing")
        return 1

    told = [e for e in expectations if e]
    print(f"OK — {len(VOICE_CASES)} voice + "
          f"{len(STAGE_DIRECTIONS) + len(NOT_STAGE_DIRECTIONS)} stage-direction + "
          f"{len(LEAK_CASES)} leak + {len(ERROR_CASES)} api-error + "
          f"{len(TALKING_CASES)} transcription + {len(ANSWER_CASES)} answer case(s) still pass, "
          f"pieces re-derived for every hand-written sentence")
    print(f"OK — session completed, {len(SPOKEN)} passages spoken, {len(steps)} model step(s) served, "
          f"{len(scripted)} turn(s) written by the code, {len(told)} listen(s) told which word to expect")
    for n in steps:
        print("    [model]   ", n.splitlines()[-1][:100])
    for target, line, _ in scripted:
        print(f"    [scripted] ({target}) {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(NO_INTRO="--no-intro" in sys.argv))
