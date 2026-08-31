"""Fills the teaching metadata (kind, gloss, pieces, literal) on content items.

The course used to carry only the Vietnamese side of each item. Everything the
tutor needed on the English side -- what the word MEANS, which pieces a
sentence is assembled from, what its literal word order is -- had to be
improvised by the model at lesson time, and measured live it improvised badly:
recalls that stated their own answer ("So how would you say là?"), rules
treated as sentences to build.

So it becomes data. Not hand-written data though: this fills it in batch, once
per content file, and is re-runnable -- it only ever touches items where a
field is missing, so new lesson files added later cost one more run and nothing
else. Review the diff, not the items one by one.

    python fill_item_metadata.py                       # show what would change
    python fill_item_metadata.py --write               # apply it
    python fill_item_metadata.py --write --limit=40    # forty per file, then stop

Run: python fill_item_metadata.py
"""
import json
import sys
import time
import tomllib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import (load_course, 
    KINDS, PERSONAL_ITEMS_FILENAME, derive_pieces, load_personal_items, load_roster,
)
from tutor import CONTENT_DIR, call_llm, load_api_key

FILL_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "set_item_metadata",
            "description": "Teaching metadata for every item you were given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": (
                                    "REQUIRED on every item, and the first thing to write: the "
                                    "Vietnamese item name, copied EXACTLY as it was given to you. "
                                    "Never leave it out and never put it in any other field -- a "
                                    "batch came back on 23 August with the name in `literal` and no "
                                    "`name` at all, and the whole request was rejected."
                                )},
                                "kind": {"type": "string", "enum": sorted(KINDS)},
                                "gloss": {
                                    "type": "string",
                                    "description": (
                                        "what it means, in English, as short as possible -- this is read aloud as "
                                        "the question ('how do you say ___?'), so it must be a natural English "
                                        "word or phrase, not a grammatical description. 'I / me', 'name', "
                                        "'to want', 'my name is ___'."
                                    ),
                                },
                                "had_to_choose": {
                                    "type": "boolean",
                                    "description": (
                                        "TRUE when the listed senses are NOT saying the same thing, so "
                                        "whichever gloss you write is one arbitrary slice of the word. "
                                        "FALSE when they are simply several English words for one "
                                        "meaning -- that is the normal case and you should just pick "
                                        "the clearest. The difference: 'near; nearby; close' is one "
                                        "meaning said three ways, so FALSE. 'to bring, to take, to "
                                        "give, to hand' is four different actions, so TRUE. 'to "
                                        "carry / to wear / to be pregnant' is TRUE. Count meanings, "
                                        "never the number of words or the number of sense lines: a "
                                        "word can have four dictionary entries and one meaning."
                                    ),
                                },
                                # No `pieces` here: repair_pieces computes it
                                # from the name before this pass runs, and asking
                                # again only invites a worse answer -- seen in
                                # the same dry run, the model offered ["không"]
                                # where the code had read ["bạn", "không"].
                                "hook": {
                                    "type": "string",
                                    "description": (
                                        "ONE true sentence of context in English, spoken just before the "
                                        "word is revealed -- or an empty string, which is the normal answer. "
                                        "The BEST hook takes a word apart into words that are themselves "
                                        "real: sân bay is sân (yard) + bay (to fly), Hà Nội is hà (river) + "
                                        "nội (inside). The learner thinks they are filing one word and files "
                                        "two, and the second sticks because it arrived inside something they "
                                        "already knew. Both halves must be genuine words -- a decomposition "
                                        "you are not sure of is exactly the invention to avoid. "
                                        "Otherwise write one where the plain template would be circular or "
                                        "flat: a word the learner already knows in English (phở, cà phê), a "
                                        "word whose origin explains its shape. It is read aloud, so keep it to one "
                                        "sentence and make it concrete. NEVER guess: if you are not certain "
                                        "the fact is true, return an empty string. An invented etymology is "
                                        "worse than no hook at all."
                                    ),
                                },
                                "literal": {
                                    "type": "string",
                                    "description": (
                                        "constructions only: the word-by-word English of the Vietnamese order, "
                                        "which is what lets a beginner produce a sentence they have never heard. "
                                        "'tôi tên là + [tên riêng]' -> 'I name is [name]'. EMPTY STRING for an "
                                        "atom, always. It is English, never the Vietnamese word -- that goes in "
                                        "`name`."
                                    ),
                                },
                            },
                            "required": ["name", "kind", "gloss"],
                        },
                    }
                },
                "required": ["items"],
            },
        },
    }
]

INSTRUCTIONS = (
    "You are annotating a Vietnamese beginner course so its tutor can ask questions from the "
    "English side instead of guessing them.\n\n"
    "kind is how the item is TAUGHT:\n"
    "  atom          one thing the learner says and is introduced as a unit. A multi-word lexical "
    "block is still an atom: 'cà phê' and 'cảm ơn' are single units, NOT assemblies.\n"
    "  construction  a sentence pattern assembled out of OTHER items in the list below. Only use "
    "this when the pieces are genuinely items already in the list.\n"
    "  rule          a fact the tutor states about the language, which the learner never says back. "
    "The name is a description, not Vietnamese speech: 'cách chọn từ xưng hô', "
    "\"tính từ không cần 'là'\". These get no pieces and no literal.\n\n"
    "gloss is spoken aloud to the learner as the question. Write the meaning, not the grammar: "
    "'I / me', not 'first person pronoun'. For a construction with a placeholder, keep the "
    "placeholder in English: 'my name is ___'.\n\n"
    "Where dictionary senses are listed, PICK ONE OF THEM rather than inventing a gloss. They come "
    "from Wiktionary and are ordered by etymology, not by use, so the FIRST is regularly the "
    "archaic or marginal reading: 'sáng' is listed first as 'a unisex given name' when it means "
    "morning, 'ngày' as a letter-case variant when it means day. Read the whole list and take the "
    "sense a beginner actually needs. Write your own only if no listed sense is usable, and some "
    "are not: a lone sense reading 'a unisex given name', 'a surname', 'Alternative letter-case "
    "form of ...' or 'onomatopoeic' is Wiktionary describing a homograph, not the word -- override "
    "it. A COUNTRY or place name is the same trap and it caught two words on 23 August: 'ý' is "
    "ranked 260 and its only senses read 'Italy', 'Italo-', 'Italian', but the word earning that "
    "rank is idea / opinion; 'vụ' is ranked 230 with the single sense 'crisis' and is really a "
    "classifier for incidents. When EVERY listed sense is a proper noun and the word is common, "
    "the dictionary has captured a homograph and missed the word -- say so by setting "
    "had_to_choose, rather than writing the proper noun. NEVER write a gloss that is a slur or an "
    "insult, whatever the dictionary lists and however high up it lists it: 'tàu' has 'Chinese; "
    "Chinaman; Chink' as its FIRST sense and the word a beginner needs is ship. Only one entry in "
    "the whole shelf is labelled a slur, so the label cannot be relied on -- read what the words "
    "actually say. The same goes when the sense CONTRADICTS "
    "the part of speech it is filed under: 'ổn' is given as an adjective with the single sense "
    "'pig', which is a noun -- the entry is for a different word, and the adjective ranked 283 "
    "means stable or fine. One sense is not a reason to trust it. Sixteen shelf items are in exactly that state, among them ngày (day), sáng (morning), "
    "vui (happy) and thành (to become).\n\n"
    "hook is almost always empty. Write one only when the item is a word the learner already "
    "knows in English, or a name that means something, or has an origin worth a sentence -- and only "
    "when you are certain it is true. A wrong fact spoken aloud is worse than a plain introduction.\n\n"
    "Some names carry an authoring label before a colon ('phủ định động từ: không + [động từ]'). "
    "The label is not spoken; gloss and literal describe what follows it.\n\n"
    "Call set_item_metadata once, with an entry for every item you were given."
)


# A grammatical word is not learned by translating it, so it is not glossed.
#
# Forty shelf items were filled as a sample and came back "be (passive)",
# "abstract noun marker", "ordinal (first, second, etc.)". Meo asked whether
# that really was all the learner would hear, and it was: shelf items carry an
# empty hook and an empty description, so the gloss is not a label beside other
# information, it IS the information. No wording fixes that. `bị` is a marker,
# and "what was be (passive)?" asks a beginner to translate terminology nobody
# taught them.
#
# 222 of the 1912 shelf items are at least partly grammatical, against 1147
# nouns, 760 verbs and 448 adjectives that gloss cleanly. The sample happened to
# be drawn from the very top of a frequency list, which is 72% function words --
# the hardest 2% of the shelf, and it would have condemned the rest with it.
#
# They stay on the shelf ungloassed, which is where they already are. What
# becomes of them -- a rule, or nothing -- is content work and not this script's.
GRAMMATICAL = frozenset({
    "particle", "pronoun", "conjunction", "preposition",
    "classifier", "determiner", "interjection", "prefix", "abbreviation",
})


# Held back by hand, because the category field could not see why. It is read
# off Wiktionary and describes whichever homograph came first, so a grammatical
# word wearing a noun's coat walks straight through GRAMMATICAL above.
#
# Kept here, with the reason, rather than as a blanked gloss: a blank gloss is
# indistinguishable from "not done yet" and the next run would fill it again.
#
# THE DUPLICATE RULE, Meo 2026-08-23: "quand t'as des doublons, on garde le
# premier et le deuxième tu le mets de côté." The first is the one already
# validated -- it has been read and kept, and the newcomer has not. Applies to
# whatever the duplicate check in content.py reports, and to the near-misses it
# cannot see, like cám ơn against cảm ơn.
#
# THE STANDING RULE, Meo 2026-08-23: "dès que tu as le moindre doute, étagère."
# A shelved word costs one line here and can be recovered in a minute. A wrong
# gloss is spoken to the learner as the whole truth about a word -- shelf items
# carry no hook and no description, so the gloss is all there is. The two are
# not comparable, so doubt resolves one way and only one way. Do not come back
# and ask; shelve it and note why.
HELD_BACK = {
    # Filed "noun, verb" because bị also means a sack. The sense that matters is
    # "particle denoting the subject is negatively affected" -- a passive marker,
    # and the sample glossed it "be (passive)", which is terminology a beginner
    # has never been taught. Same case as những and sự.
    "bị",
    # Meo, 2026-08-23: "j'ai un doute sur đưa". He is right. Its first dictionary
    # sense is "to bring, to take, to give, to hand" -- four English verbs in one
    # entry, and the filler took the first. Any single gloss is an arbitrary
    # slice. The word that actually means to give is tặng, rank 687.
    "đưa",
    # A DUPLICATE, not a doubt. dùng already carries "to use", and two words
    # answering one question means the tutor asks "what was the word for to
    # use?" and cannot be told which it wanted. Meo: "on a déjà un mot, c'est
    # ok." The rule generalises -- on 1640 words collisions are certain.
    "sử dụng",
    # Flagged as doubtful and shelved under Meo's standing rule ("dès qu'on a un
    # doute on le met de côté, puis on verra à la fin"), not by his direct call.
    # khỏi: senses run "not to have to do something", "to recover from", then
    # "to avoid" third -- the filler took the third. Same shape as đưa.
    "khỏi",
    # đều: the senses are geometry ("equal in size", "equilateral") and the
    # filler wrote "equal", but the word earns its rank 137 as an adverb meaning
    # all / both -- "chúng tôi đều thích". The dictionary gave etymology, not use.
    "đều",
    # Meo again, and the same shape as đưa: "to carry", "to wear", "to be
    # pregnant" are three different things, not three words for one thing.
    "mang",

    # --- third batch ---
    # The dictionary itself is wrong here, which no check can see. cuộc is an
    # event classifier -- cuộc họp a meeting, cuộc sống a life -- and its listed
    # senses are "to publicly demonstrate; protest", a rare homograph. The
    # filler wrote "demonstration" and did NOT flag it, because those two senses
    # ARE synonyms of each other. The pointer finds ambiguity; it cannot find a
    # gloss that is simply false.
    "cuộc",
    # A duplicate the new check caught: hôm nay already carries "today", and
    # nay's own third sense reads "Clipping of hôm nay".
    "nay",
    # Archaic and literary -- "thou". Glossed "you", which would have a beginner
    # addressing people in a register nobody has used in a century.
    "ngươi",
    # Never stands alone; it lives in xảy ra. A word the learner cannot use by
    # itself is not a word the course can ask for.
    "xảy",
    # Sound, voice, language, hour. "language" is one slice of four.
    "tiếng",
    # Grammar the category filter missed: chẳng is a negation particle and
    # bao giờ a question adverb. Same class as khi and những.
    "chẳng",
    "bao giờ",

    # --- fourth batch ---
    # The same failure as cuộc, twice more, and neither was flagged. ý is ranked
    # 260 and its only listed senses are "Italy", "Italo-", "Italian" -- the
    # proper noun Ý. The word that earns rank 260 is idea / opinion, ý kiến,
    # ý nghĩa. vụ is ranked 230 with one sense, "crisis"; it is a classifier for
    # incidents, vụ tai nạn an accident. In both the dictionary captured a
    # homograph and missed the word entirely, so the senses are internally
    # consistent and the pointer had nothing to notice.
    "ý",
    "vụ",
    # Duplicates. người already carries "person", and kẻ is pejorative anyway;
    # khiến already carries "to cause".
    "kẻ",
    "gây",
    # Two words wearing one spelling. thưa's senses read "sparse" while the
    # filler wrote "to say (politely)". câu is a sentence, or to fish, and came
    # back "story". đồng is bronze, a field, and the currency.
    "thưa",
    "câu",
    "đồng",
    # Flagged by the pointer and genuinely several things: quay turns and also
    # roasts, điểm is a point / a mark / a score, khoảng is a span and also
    # approximately, tỉnh is a province and also to wake up.
    "quay",
    "điểm",
    "khoảng",
    "tỉnh",

    # --- fifth batch ---
    # The fourth wrong dictionary entry, and the one that showed how to spot
    # them: ổn is filed as an ADJECTIVE and its single sense is "pig", a noun.
    # The category and the sense contradict each other. The real word, ranked
    # 283, means stable or fine -- "ổn không?". One sense is not a reason to
    # trust it, and the pointer had nothing to compare against.
    "ổn",
    # Its senses are "half a day" and "session, event, time, period"; the filler
    # took the second. buổi is a part of the day -- buổi sáng, buổi tối.
    "buổi",
    # dark, and also the stretch from late evening into night.
    "tối",
    # to calculate, to be of a mind, and disposition or character.
    "tính",
    # A demonstrative, so grammar -- the same class as đó, which is already
    # shelved for it. The category field said adjective and adverb.
    "kia",

    # --- sixth batch ---
    # A new shape: the ambiguity leaked INTO the gloss. Rather than choose, the
    # filler wrote both -- "rank / to grant / acute", "worthy / to deserve" --
    # which spoken becomes "what was rank or to grant or acute?", three
    # questions at once. content.py now refuses a slash with different kinds of
    # word on either side, so these two are caught automatically from now on.
    "cấp",
    "đáng",
    # The same failure the check cannot see, because likelihood and ability are
    # both nouns. Two meanings all the same.
    "khả năng",
    # bảo is to tell or to say, and "to inform" is a stiffer word for one corner
    # of it; đánh is to hit, to play an instrument, to play a game.
    "bảo",
    "đánh",

    # --- seventh batch ---
    # A duplicate the check caught: việc was glossed "job" five batches ago and
    # kept, so the newcomer goes rather than the word Meo already validated.
    "công việc",
    # A spelling variant of cảm ơn, which the course has taught since lesson one.
    # The duplicate check missed it because the glosses read differently -- "to
    # thank" against "thank you" -- so one word would have been asked two ways.
    "cám ơn",
    # thi already carries "exam", and kiểm tra's own senses say "compare thi".
    "kiểm tra",
    # to belong to, and also to know by heart.
    "thuộc",
    # to give back, and also to pay.
    "trả",

    # --- eighth batch ---
    # Its senses read "sea; ocean" and the filler wrote "sign" -- biển is a
    # signboard too, biển báo, but the word ranked here is the sea.
    "biển",
    # A completion particle: it follows a verb to mean the action is done. Same
    # class as the grammar the category filter keeps missing.
    "xong",
    # foot, and leg, and genuine.
    "chân",
    # Barely stands alone; it lives in so sánh, to compare.
    "so",

    # --- ninth batch ---
    # The duplicate check caught two pairs at once. bọn and nhóm both came back
    # "group": bọn is pejorative, a gang, so it goes and the neutral one stays.
    # khu and huyện both came back "district", and khu was kept a batch earlier,
    # so the newcomer goes -- the same call as việc against công việc.
    "bọn",
    "huyện",
    # A third and fourth word crowding the same ground: khu is a district, khu
    # vực an area, vùng a region. Four near-synonyms is more than a beginner can
    # tell apart, so the field is thinned rather than taught whole.
    "vùng",
    # permission, method, and magic; its first listed sense is "custom".
    "phép",
    # A correlative particle -- càng ... càng ..., the more ... the more. Grammar
    # the category filter missed again.
    "càng",
    # to endure, to suffer, to tolerate, to put up with, and also to agree to.
    "chịu",
    # a class of pupils, and a layer.
    "lớp",
    # Rarely alone: it lives in diễn viên and biểu diễn.
    "diễn",

    # --- tenth batch ---
    # The dictionary's FIRST sense for tàu is "Chinese; Chinaman; Chink". The
    # filler wrote "ship" and nothing reached the learner, but it is the closest
    # this has come to speaking a slur aloud. Only ONE entry in the whole shelf
    # is labelled a slur, so the label cannot be used as a filter -- the
    # instruction now says to read what the senses actually say. tàu is shelved
    # anyway, being both a ship and a train.
    "tàu",
    # Shelved before it is ever reached: its senses are "every; all" and also
    # "barbarian; savage; a racial slur" -- the one entry the dictionary does
    # label. It is the commonest word carrying that risk and it is not worth
    # the twenty recalls it would earn.
    "mọi",
    # nhóm already carries "group", and ban's first sense is "branch of
    # administration in the feudal court".
    "ban",
    # innards, and figuratively the heart. Its senses read "intestines; guts".
    "lòng",
    # expensive, and also to cross over -- sang đường, to cross the road.
    "sang",
    # excellent, from tuyệt vời, over senses reading "to cut off; to exhaust".
    "tuyệt",
    # A rural administrative unit. The same crowded field as huyện, already
    # shelved a batch ago.
    "xã",
    # Bureaucratic: a work assignment or official mission.
    "công tác",
    # to look after, and to look at.
    "trông",

    # --- eleventh batch ---
    # Three duplicates in one batch, the check's sixth, seventh and eighth
    # catches. In each the word already validated stays and the newcomer goes:
    # chờ has "to wait", bây giờ has "now", chọn has "to choose".
    "đợi",
    "hiện nay",
    "lựa chọn",
    # A genuine error, and the first of its shape. hơi's senses OPEN with
    # "slightly, somewhat, a little" -- which is the word at this frequency,
    # hơi mệt, a bit tired -- and the filler reached past it for "vapor /
    # steam". Everything else it got wrong came from the dictionary being
    # wrong; here the dictionary was right and was not read.
    "hơi",
    # degree of temperature, and also an adverb of extent.
    "độ",
    # capital as money, and also an adverb meaning originally.
    "vốn",
    # common, and also together -- chung nhau.
    "chung",

    # --- twelfth batch ---
    # Meo, on how freely to shelve: "des que t'as des doutes, erreur ou je sais
    # pas quoi: direction placard." Half this batch went, and that is the
    # intended rate rather than a bad run.
    #
    # Duplicates: chút has "a little bit", cuối has "end".
    "một chút",
    "kết thúc",
    # Each of these is two or three unrelated things wearing one spelling.
    "giải",      # a prize, to solve, to explain
    "đá",        # a rock, and to kick
    "mạng",      # a network, a spiderweb, and a life -- cứu mạng
    "sinh",      # to be born, and to produce
    "định",      # to intend; its first listed sense is a given name
    "chiều",     # afternoon, a direction, and to indulge someone
    "con trai",  # a boy, a son, and an oyster
    "khoá",      # a key, to lock, and a school term
    "vẻ",        # barely alone: it lives in vẻ đẹp, vẻ mặt
    # Glossed "to do a favour", which is what the words mean apart and not what
    # the phrase does: làm ơn is "please".
    "làm ơn",

    # --- thirteenth batch ---
    # Caught by the self-name check: glossed "Hoa people (ethnic Chinese in
    # Vietnam)", which both gives its own answer away and is not the word. hoa
    # is a flower.
    "hoa",
    # Four duplicates in one batch, the check's eleventh through fourteenth.
    # The validated word stays: tốt has "good", lớn has "big", gái has "girl",
    # thực sự has "really".
    "giỏi",
    "to",
    "con gái",
    "thật sự",
    # One spelling, unrelated things.
    "hiện",   # presently, and to appear
    "bóng",   # a shadow, and a ball
    "hội",    # a festival, and an association
    "kiếm",   # a sword, and to earn -- kiếm tiền
    "hình",   # a picture, and a shape
    # Abstract enough that no single English word reaches it.
    "cơ sở",
    "suốt",

    # --- fourteenth batch, the first of fifty ---
    # 35 of 50 kept. The ratio improves going down the frequency list, as
    # predicted: the top is function words and words with five senses, and
    # below it are rivers, aeroplanes and banks.
    #
    # Duplicates, first kept: thế has "condition", đúng has "correct",
    # thay đổi has "to change".
    "điều kiện",
    "chính xác",
    "trở",
    # Caught by the slash check -- "to laugh / smile", a verb against a noun.
    "cười",
    # Glosses that are not English: "trip / travel instance", and hề's
    # "fool / jester; to matter; completely", which is three entries in a trench
    # coat.
    "chuyến",
    "hề",
    # Two nouns either side of a slash, which the check cannot see.
    "lễ",
    # A parenthetical qualifier doing the work the gloss should do.
    "đào tạo",
    # The real thing: Vietnamese xanh covers blue AND green, which is why the
    # dictionary reaches for "grue". No English word is the answer.
    "xanh",
    # One spelling over unrelated things.
    "đông",     # east, winter, and crowded
    "thu",      # autumn, and to collect
    "nổi",      # to float, and a modal "to manage to"
    "dòng",     # a stream, and a line of text
    "rời",      # to leave, and to detach
    # Glossed "effort", a noun, for a verb meaning to try.
    "cố gắng",

    # --- fifteenth batch, the second of fifty ---
    # 36 of 50 kept. áo is another dictionary override: its listed sense is
    # "Austria" and the filler wrote "shirt".
    #
    # Duplicates, first kept: nhanh has "fast", dân has "people", tiếp tục has
    # "to continue", hy vọng has "hope". niềm was never a word for hope anyway
    # -- it is a classifier that goes in front of abstract feelings.
    "mau",
    "nhân dân",
    "tiếp",
    "niềm",
    # Caught by the length check at eight words: "to shut; to drive; to
    # solidify; to pack".
    "đóng",
    # Not vocabulary. ư is a letter of the alphabet and a final particle;
    # "game" is an English loanword whose gloss is itself, so the recall would
    # ask "what was the word for game?" and the answer would be game.
    "ư",
    "game",
    # Semicolons doing what the slash check catches, with the same fault: a verb
    # and a noun, or a noun and an adjective, offered together instead of one
    # being chosen.
    "lao động",
    "cá nhân",
    "câu chuyện",
    # Glossed "victory", a noun, for a verb meaning to win -- and its first
    # listed sense is "brake".
    "thắng",
    # to assume, and to think something mistakenly.
    "tưởng",
    # A fourth word crowding region and area, after vùng, khu and khu vực.
    "miền",
    # to hand over, to deliver, and to intersect.
    "giao",

    # --- sixteenth batch, seventy-five ---
    # 53 of 75 kept. TWELVE duplicates in one batch, which is the check
    # becoming the main filter: the course now holds 500+ glossed words, so
    # every newcomer has that many chances to collide. First kept each time.
    "tìm kiếm",    # tìm has "to look for"
    "tình trạng",  # thế has "condition"
    "hôm",         # ngày has "day"
    "toàn bộ",     # tất cả has "all"
    "thời",        # thời gian has "time"
    "Việt",        # Việt Nam has it, and Việt alone is "Yue, an ancient state"
    "triển khai",  # phát triển has "to develop"
    "trở nên",     # trở thành has "to become"
    "quận",        # khu has "district" -- the fifth word in that crowd
    "dễ dàng",     # dễ has "easy"
    "nuôi",        # nâng has "to raise"; nuôi is to raise a child, nâng to lift
    "tệ",          # xấu has "bad"
    # Not English: "time point".
    "thời điểm",
    # Institutional or political rather than vocabulary.
    "đoàn",        # the Youth Union
    "sở",          # a government department; its first sense is a camellia
    # One spelling, unrelated things.
    "trai",        # a boy, and an oyster
    "cầu",         # a bridge, to pray, and a shuttlecock
    "phát",        # to distribute, to emit, and a classifier for gunshots
    "trực tiếp",   # live, and direct
    "thay",        # to replace, and to change -- thay đổi is taught
    # Register: nhóc is familiar to the point of rude, and lũ is a flood but
    # also a dismissive classifier for a group of people.
    "nhóc",
    "lũ",

    # --- seventeenth batch, one hundred ---
    # 75 of 100 kept. Twelve duplicate groups again, first kept: viết has "to
    # write", giúp "to help", nghĩ "to think", thực hiện "to carry out",
    # thay đổi "to change", cuộc sống "life", quốc gia "country", cũ "old",
    # vua "king", thư "letter", tổng thống "president", Chúa "god".
    "ghi", "giúp đỡ", "phụ", "suy nghĩ", "tiến hành", "đổi",
    "cuộc đời", "đất nước", "chủ tịch",
    # Same word, different capitalisation.
    "chúa",
    # Worth bringing back with better glosses one day: cũ is old for THINGS and
    # già is old for PEOPLE, which the course distinguishes elsewhere and one
    # English word cannot. Shelved under the duplicate rule, not because the
    # word is bad.
    "già",
    # chữ is a written character, thư a letter you post. English "letter" covers
    # both, which is an English problem rather than a Vietnamese one.
    "chữ",
    # Glossed "king". Đức is Germany.
    "Đức",
    # A letter of the alphabet, like ư two batches ago.
    "i",
    # Plainly wrong glosses. nợ is a debt, not "to be willing". nỗi is a
    # classifier that goes in front of a feeling -- nỗi buồn, sadness -- and was
    # glossed "anger". the is a rare silk gauze.
    "nợ", "nỗi", "the",
    # Parentheticals doing the gloss's job: "time (in the past)", "subject
    # (person)".
    "hồi", "đối tượng",
    # One spelling, unrelated things.
    "khoan",  # to wait a moment, and to drill
    "băng",   # ice, a bandage, and a tape
    "hộ",     # a household, and doing something on someone's behalf
    "lối",    # a way or path, crowding đường
    "tập",    # to practise, and a volume or episode
    "bình",   # a bottle, and peaceful

    # --- eighteenth batch, one hundred ---
    # 74 of 100 kept. FIFTEEN duplicate groups, first kept each time: rất has
    # "very", học "to study", gặp "to meet", việc "job", vui "happy", tham gia
    # "to participate", dừng "to stop", ngành "industry", khu vực "area",
    # hướng "direction", may mắn "lucky", tình yêu "love", lượng "quantity",
    # điều tra "to investigate", gồm "to include".
    "vô cùng", "học tập", "họp", "việc làm", "vui vẻ", "dự", "ngừng",
    "công nghiệp", "diện tích", "đằng", "may", "tình", "số lượng",
    "tìm hiểu", "bao gồm",
    # A TONE PAIR the model got wrong, which is the first of its kind here.
    # nhắc is to remind; nhấc, one tone away, is to lift -- and "to lift" is
    # what the gloss said. The course teaches exactly this trap in its own tone
    # rules, and the tool writing the course fell into it.
    "nhắc",
    # Plainly wrong or unusable.
    "dần",   # glossed as the third earthly branch of the zodiac; it means gradually
    "đô",    # glossed "well-built"; it lives in đô la and thủ đô
    "giới",  # glossed "kingdom"; it is a world, a circle, a limit
    "liệu",  # glossed "material"; on its own it is a particle meaning whether
    # Political, and a truncated parenthetical: "party (as in Communist Party".
    "Đảng",
    # One spelling, unrelated things.
    "công",  # labour, public, merit, and a peacock
    "trò",   # a trick or game, and a pupil -- học trò
    "ca",    # a song, a work shift, and a case
    "hạ",    # to lower, and summer
    "trừ",   # to subtract, and except

    # --- nineteenth batch, cut short by an outage ---
    # Ten of thirteen batches came back "openai/gpt-oss-120b unavailable after 3
    # attempts" -- the model, not the data. Twenty-four words landed and eighty
    # were left unglossed for the next run, which is precisely what the skip
    # added five batches ago exists for: before it, one failure ended the pass
    # and threw away everything that had already succeeded.
    #
    # Duplicates, first kept: một số has "some", hệ thống "system", mạnh
    # "strong", đơn giản "simple".
    "một vài", "chế độ", "mạnh mẽ", "đơn",
    # A surname, caught by the self-name check.
    "Nguyễn",
    # south, and also Vietnam, and male, and a given name -- with Việt Nam
    # already taught.
    "Nam",
    # Legal boilerplate: a clause or an item in a contract.
    "khoản",
    # Glossed "to suck"; what it actually does is smoke -- hút thuốc.
    "hút",

    # --- twentieth batch, cut short by the same outage ---
    # Eleven of thirteen batches unavailable again. Twelve words landed.
    # Duplicates, first kept: thực phẩm has "food", chuyển "to move", rất "very".
    "thức ăn", "di chuyển", "hết sức",
    # A parenthetical doing the gloss's work: "work (a piece of art)".
    "tác phẩm",
    # An institute, and also the hospital half of bệnh viện.
    "viện",

    # --- twenty-first batch, the outage's third run ---
    # Eleven of thirteen unavailable again. Ten new words, four kept.
    # Duplicates, first kept: chiến đấu has "to fight", nhà nước has "state".
    # giành was wrong anyway -- it is to seize or to win, not to fight -- and
    # thể does not stand alone at all: it lives in cơ thể, có thể, thể thao.
    "giành", "thể",
    # north, with Nam shelved for south two runs ago and Việt Nam taught.
    "Bắc",
    # A stroke of a written character, or a facial feature.
    "nét",
    # Administrative: an area of jurisdiction.
    "địa bàn",
    # a weighing scale, to weigh, and a kilo.
    "cân",

    # --- twenty-second batch, the outage easing ---
    # Ten of thirteen unavailable rather than eleven. Twenty-four words, fifteen
    # kept: bed, voice, street, bird, mouth, poor, box, corner, occasion,
    # accident, document, Japan, to communicate.
    #
    # Duplicates, first kept: luôn has "always", loại "type", vui "happy",
    # cắt "to cut".
    "mãi", "dạng", "mừng", "chặt",
    # Political or legal register rather than vocabulary a beginner needs.
    "đồng chí",  # comrade
    "án",        # a criminal case
    "chỉ đạo",   # to direct, in the official sense
    # One spelling, unrelated things.
    "khối",      # a block, a mass, and a school year group
    "gấp",       # to fold, urgent, and a multiplier -- gấp đôi

    # --- twenty-third batch, the outage lifted ---
    # Three of thirteen unavailable rather than ten. 76 words, 55 kept.
    #
    # TWELVE duplicates, first kept each time.
    "vật", "chuẩn", "mắc", "hệ", "điều hành", "pháp luật", "thoả thuận",
    "cửa hàng", "liên tục",
    # Wrong regardless: xác is a corpse, not a body.
    "xác",
    # Two where ENGLISH is the ambiguous one, not Vietnamese -- the same shape
    # as chữ against thư for "letter". Worth returning to with better glosses.
    # nhẹ is light as in not heavy; ánh sáng is light as in illumination.
    # thị trường is an economic market; chợ is the one with stalls in it.
    "ánh sáng",
    "chợ",
    # Administrative and political register.
    "công an",   # public security
    "phường",    # a ward -- the sixth word in the district / area crowd
    "tuyến",     # a route or line, in the official sense
    # One spelling, unrelated things, or bound to a phrase.
    "đập",       # to smash, and a dam
    "dấu",       # a mark, and a tone mark
    "ký",        # to sign, and a kilo
    "hại",       # harm, but it lives in có hại
    "kèm",       # to accompany, rarely alone
    # A parenthetical doing the gloss's work: "to wash (yourself)".
    "tắm",

    # --- twenty-fourth batch, the outage back ---
    # Twelve of thirteen unavailable. Eight words, five kept: stove, sign, late,
    # to adjust, to hand in.
    # Duplicates, first kept: trường has "school", phương pháp has "method".
    "nhà trường", "biện pháp",
    # Official register: to inspect, in the government sense.
    "thanh tra",

    # --- twenty-fifth batch ---
    # Twelve of thirteen unavailable again. Eight words, six kept: code, broken,
    # in time, match, fee, serious.
    "khác biệt",  # khác has "different"
    # Glossed "imperial sacrifice ceremony". đàn is a musical instrument, or a
    # flock of animals -- the dictionary reached for a rare historical sense.
    "đàn",

    # --- twenty-sixth batch ---
    # Twelve of thirteen unavailable. Eight words, six kept: model, cheap,
    # sometimes, to contribute, to prove, sport.
    "tham dự",  # tham gia has "to participate"
    "sàn",      # tầng has "floor"

    # --- twenty-seventh batch, the window wide open ---
    # ZERO batches unavailable. A hundred words, 69 kept.
    #
    # NINETEEN duplicate groups, a record, and the reason is arithmetic: the
    # course now holds 600-odd glossed words, so a newcomer has that many
    # chances to land on a meaning already taken. First kept each time.
    "tốt đẹp", "xây", "cảm nhận", "sẵn", "trang bị", "chính quyền",
    "dĩ nhiên", "sai lầm", "ước", "tập đoàn", "trái tim", "tác động",
    "cha mẹ", "sửa", "khí", "ném",
    # Glossed "good". lương is a salary.
    "lương",
    # More of English being the vague one, not Vietnamese:
    #   cứu is to rescue; tiết kiệm is to economise -- both "to save"
    #   bác sĩ is a physician; tiến sĩ holds a doctorate -- both "doctor"
    #   lĩnh vực is a field of study; bãi is a yard or a beach -- both "field"
    "tiết kiệm", "tiến sĩ", "bãi",
    # Semicolons offering two kinds of word instead of choosing, which the
    # slash check does not see.
    "liên hệ",   # "to contact; relationship"
    "điện tử",   # "electronic; electron"
    # Too specific to be a gloss: "traditional Vietnamese poetry".
    "thơ",
    # A city, and a political name.
    "Hồ Chí Minh",
    # Bound: they live inside other words rather than standing alone.
    "tận",       # tận cùng, tận dụng
    "chuyên",    # chuyên gia, chuyên nghiệp
    # One spelling, unrelated things.
    "bầu",       # a gourd, to elect, and pregnant
    "phân",      # fertiliser, to divide, and a part
    "dịch",      # to translate, an epidemic, and a fluid
    "la",        # to shout, a mule, and the note A
    "tướng",     # a general, and a physiognomy

    # --- twenty-eighth batch, the second full window ---
    # A hundred words, 57 kept. TWENTY-SEVEN duplicate groups, up from
    # nineteen: the course crossed 700 glossed words between the two runs, and
    # the collision rate is following the size of what is already taught.
    "xinh đẹp", "phương tiện", "con số", "hàng hoá", "thương", "gia",
    "đô thị", "màu sắc", "đời sống", "tổ", "nhất định", "động", "địa điểm",
    "nêu", "thích hợp", "giấu", "quan", "đại biểu", "ngã", "hợp",
    "chào mừng", "vì thế", "ánh", "phức tạp", "văn bản", "đóng góp", "đua",
    # Slashes joining two unrelated things. The slash check does NOT catch
    # these -- it only separates a verb from a non-verb, and "temple / free",
    # "high-class / superior", "to approach / to reach" all have the same kind
    # of word on both sides. Named here because I said I would write a check on
    # the next occurrence and cannot: telling "I / me" from "temple / free"
    # needs to know what the words MEAN.
    "chùa", "cao cấp", "tiếp cận",
    # Caught by the length check at seven words: "to stick / to be involved in".
    "dính",
    # Compositional or over-specified: lái and xe are both taught, mở and cửa
    # are both taught, and "to compete athletically" puts an adverb in a gloss.
    "lái xe", "mở cửa", "thi đấu",
    # Institutions of state.
    "quốc hội", "trung ương", "uỷ ban", "bộ trưởng",
    # One spelling, unrelated things.
    "đề",    # an exam question, and a topic
    "sát",   # close, and to kill -- sát hại
    "cung",  # a palace, a bow, and to supply
    # Nhật Bản already carries Japan.
    "Nhật",

    # --- twenty-ninth batch, third full window ---
    # A hundred words, 67 kept. Eighteen duplicate groups.
    "luôn luôn", "thông thường", "đội ngũ", "khám phá", "nhầm", "để ý",
    "kỹ", "ngoại", "chủ đề", "cuộc chiến", "cho nên", "tín hiệu", "trễ",
    "nghiêm trọng", "tuyên bố",
    # Three more where ENGLISH is the vague one. Each pair is a real
    # distinction Vietnamese makes and English does not, and each is worth
    # returning to when a gloss can carry it:
    #   cơm is cooked rice, lúa is the plant growing in the field
    #   đầy is a full container, no is full from eating
    #   mặc is to wear clothes, đeo is to wear a watch or glasses
    "lúa", "no", "đeo",
    # Not vocabulary: a letter of the alphabet, and a city abroad. Both caught
    # by the self-name check.
    "u", "New York",
    # Vietnamese place name, the same call as Hồ Chí Minh.
    "Đà Nẵng",
    # Wrong. thức is to stay awake; bảo đảm was glossed "to sponsor" and means
    # to guarantee, which đảm bảo -- the same two syllables reversed -- already
    # carries.
    "thức", "bảo đảm",
    # Bound: they live inside longer words.
    "đại",   # đại học, đại diện
    "châu",  # châu Á, châu Âu
    "tạm",   # tạm thời
    "khai",  # khai báo, khai thác
    # One spelling, unrelated things.
    "lợi",    # profit, and a gum in the mouth -- with lợi ích taught
    "trống",  # a drum, and empty
    "hạng",   # a class, and a rank
    # ngốc already carries foolish.
    "ngu ngốc",
    # Institutional, and kế hoạch already carries plan.
    "thủ tướng", "quy hoạch",

    # --- thirtieth batch, fourth full window ---
    # A hundred words, 63 kept. Eighteen duplicate groups.
    "chờ đợi", "bàn tay", "bớt", "mức độ", "phương", "độc đáo", "xưa",
    "tỏ", "nghỉ ngơi", "tồi tệ", "tâm", "thôn", "đấu", "tình huống",
    "chiến", "đỡ", "đỉnh", "xét",
    # The slash check earned its keep three times in one batch, all verbs
    # against non-verbs: "to skip / ignore", "to update / keep posted",
    # "to arrange / organize".
    "bỏ qua", "cập nhật", "sắp xếp",
    # And two it still cannot see, both nouns on either side: "basement /
    # cellar", "faculty / department".
    "hầm", "khoa",
    # Not words at all. hoá is a suffix -- the -ise of hiện đại hoá. g is a
    # letter, caught by the self-name check. tí was glossed "Rat", the zodiac
    # sign. sam is a horseshoe crab, which no beginner needs before a thousand
    # other words.
    "hoá", "g", "tí", "sam",
    # Archaic and faintly disdainful: ả for an older woman.
    "ả",
    # Bound, or awkwardly glossed.
    "nghiệm",     # kinh nghiệm, thí nghiệm
    "phiên",      # phiên bản, phiên họp
    "sinh hoạt",  # glossed "non-work activities"
    # Place names, with Mỹ already carrying America and Bắc already shelved.
    "Hoa Kỳ", "Tây", "bắc",
    # One spelling, unrelated things.
    "dạo",   # a stretch of time, and to stroll
    "lạc",   # lost, and a peanut
    "hành",  # a scallion, and to act

    # --- thirty-first batch, a partial window ---
    # Seven of thirteen unavailable. 48 words, 31 kept.
    "tuyển", "xử", "bang", "tham quan", "thùng", "tiết",
    # Capitalisation variant of Tết, already taught.
    "tết",
    # English again: báo chí is the press as in newspapers, nhấn is to press a
    # button. ép is to press as in squeeze -- three unrelated things wearing one
    # English word.
    "nhấn", "ép",
    # Bound: they live inside longer words.
    "thủ",  # thủ đô, thủ tướng
    "cử",   # cử tri, bầu cử
    "tài",  # tài chính, tài liệu, tài khoản
    # Vietnamese place names, the same call as Hồ Chí Minh and Đà Nẵng.
    "Huế", "Sài Gòn",
    # One spelling, unrelated things, or too narrow.
    "chà",      # to brush, and an interjection
    "đậu",      # a bean, to park, and to pass an exam
    "cổ phần",  # equity, in the financial sense

    # --- thirty-second batch ---
    # Ten of thirteen unavailable. 24 words, 14 kept. Six duplicates.
    "mệt mỏi", "sắc", "quản trị", "lộ", "tổng hợp", "nối",
    # Bound: hưởng lives in ảnh hưởng and hưởng thụ.
    "hưởng",
    # Compositional -- đóng and cửa are both taught, so "close the door" is a
    # sentence the learner can already build rather than a word to learn.
    "đóng cửa",
    # quần áo already carries clothes.
    "trang phục",
    # Abstract, and nhận is already shelved.
    "nhận thức",

    # --- thirty-third batch ---
    # Seven of thirteen unavailable. 48 words, 33 kept. Six duplicates.
    "tập thể", "động vật", "phạm", "chứng", "thí nghiệm", "cỡ",
    # Caught by the slash check: "to roast / grill", a verb against a noun.
    "nướng",
    # Caught by the self-name check: glossed "Đông (a personal name)".
    "Đông",
    # Institutional, and đoàn is already shelved for the same reason.
    "Đoàn",
    # yêu already carries to love; "to love and cherish" is two verbs.
    "yêu thương",
    # Bound, or one spelling over unrelated things.
    "xứ",         # xứ sở, đất nước
    "chiếu",      # to shine, a sleeping mat, and to project a film
    # Financial or narrow, with cổ phần already shelved for the same field.
    "cổ phiếu", "tín dụng",
    # Glossed "to terrify"; the word is terrorism.
    "khủng bố",

    # --- thirty-sixth batch, twenty words after a pause ---
    # Zero failures, after two runs where all thirteen batches returned 403.
    # Six duplicates: phát triển has "to develop", xây dựng "to build",
    # học sinh "student", sông "river", lực lượng "force", ngăn "to block".
    "phát huy", "dựng", "học viên", "lực", "chặn",
    # And thông was glossed "river", which is not what it means -- a pine tree,
    # or to be clear through. The duplicate check caught it for the wrong
    # reason and was right anyway.
    "thông",
    # Two nouns either side of a slash, which the slash check cannot see:
    # "hair / fur / feathers".
    "lông",
    # One spelling, unrelated things.
    "khớp",  # a joint in the body, and to match
    "độc",   # poisonous, and single -- độc thân

    # --- thirty-seventh batch, fifty words, still no 403 ---
    # Seven batches instead of thirteen, and the block has not come back.
    # Duplicates, first kept: ngày mai has "tomorrow", thật "real", mức
    # "level", bí mật "secret", chữa "to repair", vay "to borrow", chở "to
    # transport".
    "mai", "thực", "trình độ", "kín", "sửa chữa", "mượn", "vận chuyển",
    # Caught by the self-name check, and a brand besides.
    "Google",
    # A personal name, and an ethnic group -- người Kinh.
    "Hùng", "kinh",
    # Place names.
    "Ấn Độ", "Á",
    # Bound, or one spelling over unrelated things.
    "xuyên",  # xuyên qua
    "đáp",    # trả lời already carries to reply
    "lát",    # a slice, and a moment -- một lát
    "hương",  # a fragrance, incense, and a given name
    "phủ",    # to cover, and a government office

    # --- thirty-eighth batch, a hundred again and still no 403 ---
    # Thirteen batches, which is what was blocked twice earlier, and it went
    # through. So the block was the evening's cumulative volume rather than the
    # size of one run.
    #
    # Sixteen duplicates, first kept. mặt beat BOTH khuôn mặt and gương mặt for
    # "face", the first three-way group in a while.
    "thiệt", "trường học", "lưu", "gia tăng", "khuôn mặt", "gương mặt",
    "phương án", "cứng", "phiếu", "sân khấu", "quyền lực", "trẻ con",
    "tiêu thụ", "địch", "thợ", "miêu tả",
    # This batch produced far more multi-alternative glosses than any before,
    # and the checks took all of them -- four by the slash rule and four by
    # length. diện came back as "to dress up / well-dressed / aspect / area /
    # sphere", which is eleven words and five meanings.
    "diện", "tiêu diệt", "giải phóng", "phân phối",
    "kích thích", "hầu hết", "quyến rũ",
    # Caught by the self-name check.
    "web",
    # More of the same shape the checks could not see -- same kind of word on
    # both sides of the slash.
    "vừa mới", "ngược", "cơ chế", "đau đớn",
    # tin already carries news.
    "tin tức",
    # Three words in one field; nguyên liệu keeps it.
    "vật chất", "vật liệu",
    # Parenthetical doing the gloss's work, or compositional.
    "nhiễm",    # "to contract (an illness)"
    "ăn uống",  # ăn and uống are both taught
    # Tây is already shelved for west.
    "tây",
    # Bound, or one spelling over unrelated things.
    "văn",   # văn học, văn hoá, văn bản
    "bi",    # a marble, and tragic
    "lao",   # to plunge, tuberculosis, and labour
    "mạch",  # a circuit, and a pulse
    # Military rank, narrow.
    "đại tá",

    # --- thirty-ninth batch, the last hundred ---
    # Twenty duplicate groups, first kept each time.
    "cực kỳ", "giờ đây", "mặt hàng", "Hoàng", "rắn", "Trung", "giảng dạy",
    "quy trình", "chức", "lầu", "sốt", "tiệm", "xuất", "chứng khoán",
    "con cái", "ra lệnh", "mọc", "bố trí", "đại uý", "thách thức",
    # Not words a beginner can use. canh was glossed "seventh heavenly stem",
    # from the sexagenary calendar. hi is a grin written as a syllable. ben is
    # a dump truck, from the French benne. khúc was glossed "firewood" and is a
    # segment or a stretch.
    "canh", "hi", "ben", "khúc",
    # Institutional, or bound inside longer terms.
    "chủ nghĩa",     # chủ nghĩa xã hội
    "công đoàn",
    "phó chủ tịch",  # chủ tịch is already shelved
    "mục",           # mục tiêu, mục đích
    # A third word in the material field, where nguyên liệu keeps it.
    "chất liệu",
    # Narrow, or one spelling over unrelated things.
    "hạt nhân",
    "trần",  # bare, and a ceiling
}


def _is_grammatical(raw: dict) -> bool:
    if raw.get("name") in HELD_BACK:
        return True
    parts = {p.strip().lower() for p in (raw.get("category") or "").split(",")}
    return bool(parts & GRAMMATICAL)


def _needs_fill(raw: dict) -> bool:
    """True if anything is still missing. Constructions need more than atoms,
    but kind is what says so -- and kind itself may be what is missing, so an
    item with no kind always counts as incomplete."""
    if _is_grammatical(raw):
        return False
    if "kind" not in raw or not raw.get("gloss"):
        return True
    # `pieces` is deliberately not checked here: repair_pieces derives it
    # offline just above, so a construction missing it is not a model's job.
    if raw["kind"] == "construction" and not raw.get("literal"):
        return True
    return False


# Items per request. Groq's free tier allows ~8000 tokens a minute and each
# item carries a paragraph of Vietnamese notes, so a whole file in one call
# blows the budget -- measured: 25 items in one request 429'd through every
# retry. Small batches also mean a rate limit costs one batch, not a file.
BATCH_SIZE = 8

# And spaced out. The retry backoff alone was not enough: a batch costs roughly
# a third of the minute's tokens, so back-to-back batches ran the bucket dry and
# a whole file died partway through. Waiting is free here -- this is an offline
# authoring pass, not a lesson anybody is sitting through.
SECONDS_BETWEEN_BATCHES = 30


def _ask(api_key: str, targets: list[dict], all_names: list[str]) -> dict[str, dict]:
    """Metadata for every target, keyed by item name, in paced batches."""
    out: dict[str, dict] = {}
    for start in range(0, len(targets), BATCH_SIZE):
        batch = targets[start:start + BATCH_SIZE]
        if start:
            time.sleep(SECONDS_BETWEEN_BATCHES)
        print(f"  ({start + 1}-{start + len(batch)} of {len(targets)}...)")
        # One bad batch must not kill the run. On 23 August a batch came back
        # with `name` missing on all eight items -- the model had put the
        # Vietnamese into `literal` -- and the 400 propagated all the way out,
        # ending the pass and writing nothing. Over the 239 batches this file
        # still needs, a single malformed answer would throw away everything
        # before it. The items are simply left unglossed, which is a state the
        # course already handles, and the next run picks them up.
        try:
            out.update(_ask_batch(api_key, batch, all_names))
        except (RuntimeError, KeyError, ValueError) as e:
            names = ", ".join(t["name"] for t in batch)
            print(f"  !! this batch failed and was skipped -- {type(e).__name__}: {str(e)[:160]}")
            print(f"     left unglossed, will be retried next run: {names}")
    return out


# The catalogue of every name in the course goes in so the model can resolve a
# CONSTRUCTION's pieces -- "a sentence pattern assembled out of OTHER items in
# the list below". Nothing else in the job needs it.
#
# At 2133 names it is ~8947 tokens against a free-tier ceiling of 8000 a minute:
# on its own, 111% of a minute's budget before one word to be glossed is added.
# So this script stopped running the day the frequency shelf was imported --
# silently, while the startup banner went on recommending it. BATCH_SIZE could
# have gone to 1 and it would still have failed.
#
# It is sent only when a batch can use it. The shelf -- 1912 items, every one
# kind=atom, none with pieces -- never can. Its 867 multi-word compounds are the
# one case that might, and content.derive_pieces already derives those from the
# name in code, which is where it belongs.
def _needs_catalogue(targets: list[dict]) -> bool:
    """True unless every item is already known to be a plain atom.

    An item whose `kind` is missing is what this script is here to decide, so it
    may yet turn out to be a construction: those keep the catalogue. Only an
    item that already SAYS it is an atom can go without.
    """
    return not all(t.get("kind") == "atom" for t in targets)


def _ask_batch(api_key: str, targets: list[dict], all_names: list[str]) -> dict[str, dict]:
    catalogue = ("\n".join(f"{n}. {name}" for n, name in enumerate(all_names, 1))
                 if _needs_catalogue(targets) else "")
    # The senses come from Wiktionary via import_frequency_words.py, which
    # deliberately does NOT pick one -- its docstring explains they are ordered
    # by etymology, so the first is routinely the archaic reading ("là" as "fine
    # silk", "tôi" as "slave; domestic servant"). It left the choosing to this
    # script, and this script was never given the list: `senses` appeared nowhere
    # here, so 1915 shelf items were being glossed from the Vietnamese word and a
    # part of speech, with the dictionary four lines away in the same file.
    described = "\n\n".join(
        f"{t['name']}\n  category: {t.get('category', '?')}\n"
        f"  dictionary senses: {' | '.join(t.get('senses') or []) or '(none listed)'}\n"
        f"  notes (Vietnamese): {t.get('description', '')}"
        for t in targets
    )
    response = call_llm(
        api_key,
        [
            {"role": "system", "content": INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    (f"The whole course, in teaching order:\n{catalogue}\n\n" if catalogue else "")
                    + f"Annotate exactly these {len(targets)} items:\n\n{described}"
                ),
            },
        ],
        tools=FILL_TOOL,
    )
    calls = response["choices"][0]["message"].get("tool_calls") or []
    if not calls:
        raise RuntimeError("the model answered without calling set_item_metadata")
    out: dict[str, dict] = {}
    for call in calls:
        for entry in json.loads(call["function"]["arguments"])["items"]:
            out[entry["name"]] = entry
    return out


def _clean(entry: dict, known_names: set[str]) -> dict:
    """Keeps only what belongs on this kind of item.

    `pieces` is not among them -- repair_pieces owns that field now, and letting
    this pass write it too would undo the derivation with a worse guess.
    """
    kind = entry.get("kind", "atom")
    if kind not in KINDS:
        kind = "atom"
    fields = {"kind": kind, "gloss": entry.get("gloss", "").strip(),
              "hook": (entry.get("hook") or "").strip()}
    if kind == "construction":
        fields["literal"] = entry.get("literal", "").strip()
    return fields


def _toml_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _insert_into_toml(text: str, name: str, fields: dict) -> str:
    """Inserts the new keys straight after the item's `name =` line.

    Targeted text insertion rather than a re-serialised TOML: it keeps the
    files' comments and formatting exactly as authored. It RAISES when the
    anchor line is not found or is ambiguous -- a bulk replacement that
    silently matches nothing has cost this project a round of live testing more
    than once, and a no-op here would look like a successful run.
    """
    anchor = f"name = {_toml_value(name)}"
    lines = text.splitlines(keepends=True)
    hits = [n for n, line in enumerate(lines) if line.strip() == anchor]
    if len(hits) != 1:
        raise RuntimeError(f"anchor {anchor!r}: expected exactly one line, found {len(hits)}")
    at = hits[0]

    # An EXISTING key is rewritten in place, not shadowed by a second one.
    # The lesson files simply omit a field they have not got, so inserting was
    # always enough there. The frequency shelf was imported with `gloss = ""`
    # present and empty, and _needs_fill picks exactly those -- so every one of
    # the 1912 shelf items would have come out with two `gloss` lines and the
    # file would no longer parse. Found on a 16-item sample before --write ever
    # touched the real one.
    end = next((n for n in range(at + 1, len(lines))
                if lines[n].strip() == "[[items]]"), len(lines))
    eol = "\r\n" if lines[at].endswith("\r\n") else "\n"
    pending = {}
    for key, val in fields.items():
        written = f"{key} = {_toml_value(val)}{eol}"
        existing = next((n for n in range(at + 1, end)
                         if lines[n].lstrip().startswith(f"{key} = ")), None)
        if existing is None:
            pending[key] = written
        else:
            lines[existing] = written
    if pending:
        lines.insert(at + 1, "".join(pending.values()))
    return "".join(lines)


def _report(path: Path, name: str, fields: dict) -> None:
    print(f"  {name}")
    for key, val in fields.items():
        print(f"      {key} = {_toml_value(val)}")


def fill_toml(path: Path, api_key: str, all_names: list[str], write: bool,
              limit: int | None = None) -> int:
    text = path.read_text(encoding="utf-8")
    raws = tomllib.loads(text).get("items", [])
    targets = [r for r in raws if _needs_fill(r)]
    if not targets:
        print(f"{path.name}: nothing missing")
        return 0
    # The frequency shelf is 1912 items, which is 239 batches and about two
    # hours. Nobody should have to spend that before seeing whether the glosses
    # are any good -- and since the run only ever fills what is still empty, it
    # is resumable: forty now, forty later, and the ones already done are
    # skipped by _needs_fill.
    remaining = len(targets)
    if limit is not None:
        targets = targets[:limit]
    print(f"{path.name}: filling {len(targets)} item(s)"
          + (f" of {remaining} still missing" if limit is not None and remaining > len(targets) else ""))
    filled = _ask(api_key, targets, all_names)
    known = set(all_names)
    chose = []
    for raw in targets:
        entry = filled.get(raw["name"])
        if entry is None:
            print(f"  !! {raw['name']}: the model returned nothing for this one, left as is")
            continue
        if entry.get("had_to_choose"):
            chose.append((raw["name"], (entry.get("senses") or raw.get("senses") or [""])[0]))
        fields = {k: v for k, v in _clean(entry, known).items() if k not in raw or not raw.get(k)}
        if not fields:
            continue
        _report(path, raw["name"], fields)
        text = _insert_into_toml(text, raw["name"], fields)
    # It POINTS, it does not block. Measured on eight words with known answers:
    # it flagged all three that genuinely needed it -- đưa, mang, khỏi -- and
    # three of the five that did not, gần, nhà and tay. Perfect recall, poor
    # precision. Blocking on that would have shelved most of a good batch;
    # pointing at 60% false alarms still saves reading the other two thirds.
    #
    # Asked of the model rather than counted, because counting cannot tell
    # synonyms from meanings: "3+ alternatives" would shelve gần ("near;
    # nearby; close") and "3+ senses" would have shelved eight of the
    # twenty-two Meo had just validated, nhà "house" and giờ "hour" among them.
    if chose:
        print(f"\n  Look at these {len(chose)} first -- the model says the senses are not "
              f"saying one thing, so its gloss is one slice of the word:")
        for name, first in chose:
            print(f"     {name:14} {first[:70]}")
        print("  Glossed anyway. Shelve the ones you agree with by adding them to HELD_BACK.\n")
    if write:
        path.write_text(text, encoding="utf-8")
    return len(targets)


def fill_json(path: Path, api_key: str, all_names: list[str], write: bool) -> int:
    entries = json.loads(path.read_text(encoding="utf-8"))
    targets = [e for e in entries if _needs_fill(e)]
    if not targets:
        print(f"{path.name}: nothing missing")
        return 0
    print(f"{path.name}: filling {len(targets)} item(s)")
    filled = _ask(api_key, targets, all_names)
    known = set(all_names)
    for raw in targets:
        entry = filled.get(raw["name"])
        if entry is None:
            print(f"  !! {raw['name']}: the model returned nothing for this one, left as is")
            continue
        fields = {k: v for k, v in _clean(entry, known).items() if k not in raw or not raw.get(k)}
        if not fields:
            continue
        _report(path, raw["name"], fields)
        raw.update(fields)
    if write:
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(targets)


def repair_pieces(personal: Path, roster: list, write: bool) -> int:
    """Recomputes `pieces` on every generated construction, offline.

    Runs before anything else and costs no request: pieces are read off the
    name against the roster, never asked of a model. That is the whole point --
    measured on this file, the model got 8 of its 13 constructions wrong, one
    declaring a single piece for an eight-word sentence and one declaring none.

    Only the generated file is touched. Hand-written TOML stays authoritative:
    derive_pieces reproduces all five of its constructions exactly, so there is
    nothing to repair there and no reason to let code overwrite an author.
    """
    if not personal.exists():
        return 0
    entries = json.loads(personal.read_text(encoding="utf-8"))
    changed = 0
    for entry in entries:
        if entry.get("kind") != "construction":
            continue
        derived = derive_pieces(entry["name"], roster)
        if derived != entry.get("pieces"):
            print(f"  {entry['name']}")
            print(f"     was  {entry.get('pieces')}")
            print(f"     now  {derived}")
            entry["pieces"] = derived
            changed += 1
    if changed and write:
        personal.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{personal.name}: {changed} construction(s) re-derived")
    return changed


def main() -> int:
    write = "--write" in sys.argv
    # --limit N stops after N items PER FILE. The shelf alone is 1912, which is
    # about two hours, and nobody should spend that before reading a sample.
    # Resumable, because a run only ever fills what is still empty.
    limit = next((int(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--limit=")), None)
    api_key = load_api_key()
    lesson_files = sorted(p for p in CONTENT_DIR.glob("*.toml") if p.name != "persona.toml")
    personal = CONTENT_DIR / PERSONAL_ITEMS_FILENAME

    # Every name in the course, in teaching order: pieces may only reference
    # items that exist, and the model needs the whole catalogue to resolve them
    # even while annotating one file at a time.
    all_names = []
    for path in lesson_files:
        all_names += [r["name"] for r in tomllib.loads(path.read_text(encoding="utf-8")).get("items", [])]
    if personal.exists():
        all_names += [e["name"] for e in json.loads(personal.read_text(encoding="utf-8"))]

    # Offline and free, so it goes first and always: no point paying a model to
    # annotate items whose structural field is wrong.
    total = repair_pieces(personal, load_course(CONTENT_DIR), write)

    total += sum(fill_toml(path, api_key, all_names, write, limit) for path in lesson_files)
    if personal.exists():
        total += fill_json(personal, api_key, all_names, write)

    if not write:
        print(f"\n{total} item(s) would change. Re-run with --write to apply.")
    else:
        print(f"\n{total} item(s) written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
