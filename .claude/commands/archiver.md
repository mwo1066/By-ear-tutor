---
description: Fold a finished change into SPEC.md and into the journal
argument-hint: <change number, e.g. 0003>
---

Change: $ARGUMENTS

1. Read `changes/$ARGUMENTS-*/proposition.md`. **Refuse to archive** if any tasks
   are still unticked: say which ones.
2. **Fold the delta into `SPEC.md`.** For each rule announced: add, modify or
   remove it, keeping the file's shape — the numbered title, the **Where:** line
   (code or prompt), the **Why** when there is a real reason to keep, the
   **Change:** line with the file and the symbols. The **Why** is justified by an
   observed failure, never by an intention.
3. **Check what you write against the code**, not against the proposal: the
   proposal said what was wanted, the code says what is. Where the two differ,
   the code is right, and the difference goes into `Result`.
4. Add the `Result` section to the proposal: date, commits, what was done
   differently from the plan, what was tried and abandoned on the way.
5. Move the folder into `changes/archive/` (`git mv`, to keep the thread).
6. Add the line at the top of "Archived changes" in
   `changes/archive/JOURNAL.md`. If the change undid something earlier, add the
   row to the "tried **and undone**" table as well.
7. Update `STATUS.md` if the working state of the project has moved.
