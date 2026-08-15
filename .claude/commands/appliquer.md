---
description: Implémenter un changement proposé, en cochant ses tâches
argument-hint: <numéro du changement, ex. 0003>
---

Changement : $ARGUMENTS

1. Lis `changes/$ARGUMENTS-*/proposition.md`. Si le numéro est ambigu ou absent,
   liste ce qu'il y a dans `changes/` et arrête-toi.
2. Passe le **Statut** à `en cours`.
3. Fais les tâches **dans l'ordre**, en cochant `- [x]` au fur et à mesure dans
   le fichier — pas à la fin.
4. **Si la réalité diverge de la proposition** — le code n'est pas là où elle le
   dit, une tâche en révèle une autre, la solution prévue ne marche pas —
   **arrête-toi et dis-le.** N'improvise pas une autre version en silence : la
   proposition est ce que l'utilisateur a accepté. Il décide si on la corrige ou
   si on change d'approche.
5. Ne touche pas à `SPEC.md` ici. C'est `/archiver` qui le fait, une fois que ce
   qui a été fait est connu.
6. Lance la vérification écrite dans la proposition, `python smoke_test.py` au
   minimum. **Rapporte la sortie telle quelle**, y compris si elle échoue.
7. Note au fil de l'eau, en bas du fichier, ce qui s'est passé autrement que
   prévu — ça deviendra la section `Résultat`.
