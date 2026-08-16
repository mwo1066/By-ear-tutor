---
description: Re-read the code and list what SPEC.md claims and it no longer does
---

**You change nothing.** The deliverable is a drift report.

1. Read `SPEC.md` in full.
2. For each rule, go and check in the code what it announces — in particular the
   symbols named on the **Change:** line. A rule whose symbol no longer exists is
   drift, even if the behaviour still holds elsewhere.
3. Classify what you find:
   - **False** — the rule claims a behaviour the code no longer produces.
   - **Misplaced** — the rule is right, but the **Where:** line says code when it
     is the prompt, or the reverse. This is the most expensive drift: an
     announced guarantee that is only an instruction.
   - **Stale** — the files or symbols on **Change:** no longer exist.
   - **Missing** — the code guarantees a behaviour `SPEC.md` mentions nowhere.
4. Report by rule number, with the file and the line, worst first. No fixes: each
   drift is either an obvious correction to make immediately on request, or a
   proposal to open with `/proposer`. Say which of the two, for each one.
