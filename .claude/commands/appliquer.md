---
description: Implement a proposed change, ticking off its tasks
argument-hint: <change number, e.g. 0003>
---

Change: $ARGUMENTS

1. Read `changes/$ARGUMENTS-*/proposition.md`. If the number is ambiguous or
   missing, list what is in `changes/` and stop.
2. Set the **Status** to `in progress`.
3. Do the tasks **in order**, ticking `- [x]` as you go in the file — not at the
   end.
4. **If reality diverges from the proposal** — the code is not where it says, one
   task reveals another, the planned solution does not work — **stop and say
   so.** Do not improvise a different version in silence: the proposal is what
   the user accepted. They decide whether to fix it or change approach.
5. Do not touch `SPEC.md` here. `/archiver` does that, once what was actually
   done is known.
6. Run the verification written in the proposal, `python smoke_test.py` at
   minimum. **Report the output as it is**, including when it fails.
7. Note as you go, at the bottom of the file, what happened differently from the
   plan — that will become the `Result` section.
