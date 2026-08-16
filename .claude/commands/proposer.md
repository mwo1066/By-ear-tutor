---
description: Write a change proposal, without touching the code
argument-hint: <the idea, in one sentence>
---

The idea: $ARGUMENTS

**You write no code during this command.** The deliverable is a proposal file,
nothing else.

1. **Read `changes/archive/JOURNAL.md` in full.** If the idea is in there — done,
   or tried and then undone — say so first, with the commit and what it gave. Do
   not propose redoing it without addressing the reason it was taken out.
2. Read `changes/README.md` (the template and the scope test), then the rules of
   `SPEC.md` concerned.
3. **Check in the code** that the problem exists as described. A proposal's "Why"
   is an observation, not a supposition. If you cannot observe it, write that in
   its place.
4. **Apply the scope test** from `changes/README.md`. If the change contains two,
   **propose the split before writing**: the titles of the two or three changes,
   which goes first, and why that order. Wait for the answer.
5. Write `changes/NNNN-short-name/proposition.md` — `NNNN` = the largest existing
   number in `changes/` and `changes/archive/`, plus one, four digits. Follow the
   template without changing its sections.
6. For each rule touched, say **code** or **prompt**, and if it is the prompt:
   what it removes from it, or why the code cannot do it.
7. End your reply with the path of the file and the points you want a decision
   on — not with a summary of what you have just written.

Consult `STYLE.md` if the idea is about how the tutor speaks: it may already have
a drawer there, or already be waiting to be measured.
