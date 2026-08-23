# A rule turn hands over without inviting speech

**Status:** done.
**Opened:** 2026-08-23

## Why

Two people were stopped by the same turn, on two different evenings, and one of
them is a native speaker.

The `rule` turn for `trăm nghìn` said:

> The notes you actually hold are hundreds of thousands — một trăm nghìn.
> two hundred thousand — hai trăm nghìn. five hundred thousand — năm trăm nghìn.
> **Your turn.**

Meo, live: *"bah ici on sait même pas quoi il demande."* On the earlier session
the identical shape produced *"Which one I have to said?"* The native speaker
guessed and said `Trăm nghìn`.

**And the model is doing exactly what it was told.** The step's instruction ends:

> *"Ask NOTHING: the next turn does the asking. End on a short line that hands
> over, ..."*

That line was written to stop the rule turn leaking the answer, and at that job
it works — the leak it was fighting is gone. But "a short line that hands over"
becomes **"Your turn."**, which invites the learner to speak while naming
nothing to say. They answer into a void, and the real question — the one the
code writes — arrives a turn later against an answer already given.

So this is not the model misbehaving. It is an instruction that solved one
problem and created the next one.

## What is proposed

**The rule turn ends without inviting speech at all.** It tells, and it stops.
No "Your turn.", no "Now you try.", nothing in the second person that asks for a
voice. The next step is scripted, it asks properly, and it is the only place a
question belongs.

Meo's own framing was *"un exemple à la fois"* — asking one thing rather than
listing three and pointing vaguely. Ending the telling turn cleanly is what
makes that true: the code's next turn already asks one thing.

## Checked first, and it came back clean

What follows a `rule` step, counted over every plan in the course:

```
   41x  recall_piece
   22x  rapidfire
    5x  apply
   ---
   68 of 68, and all three are in SCRIPTED_KINDS
```

**Never a model turn, never the end of an item.** So there is nothing for the
rule turn to hand over to that is not already about to ask, plainly, in words
the code wrote. Removing the invitation removes a problem and creates none.

## Not in this change

The tutor announcing failure ("That's not it.") — a separate observation, its
own fix, and `0024`.

Two further defects seen the same evening are **knowingly left**, on Meo's call:
the answer being given away before being asked, and Vietnamese landing
mid-sentence. Both are recorded in `notes/OPEN.md`. Meo: *"le reste je m'en
rappelle plus, on ne fait pas — on corrigera peut-être si je repasse dessus."*
