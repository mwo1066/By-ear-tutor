---
description: Replier un changement terminé dans SPEC.md et dans le journal
argument-hint: <numéro du changement, ex. 0003>
---

Changement : $ARGUMENTS

1. Lis `changes/$ARGUMENTS-*/proposition.md`. **Refuse d'archiver** s'il reste
   des tâches non cochées : dis lesquelles.
2. **Replie le delta dans `SPEC.md`.** Pour chaque règle annoncée : ajoute,
   modifie ou supprime, en gardant la forme du fichier — le titre numéroté, la
   ligne **Où :** (code ou prompt), le **Pourquoi** quand il y a une vraie
   raison à retenir, la ligne **Changer :** avec le fichier et les symboles.
   Le **Pourquoi** se justifie d'un échec observé, jamais d'une intention.
3. **Vérifie ce que tu écris contre le code**, pas contre la proposition : la
   proposition disait ce qu'on voulait, le code dit ce qui est. Là où les deux
   diffèrent, c'est le code qui a raison, et la différence va dans `Résultat`.
4. Ajoute la section `Résultat` à la proposition : date, commits, ce qui a été
   fait autrement que prévu, ce qui a été essayé et abandonné en route.
5. Déplace le dossier dans `changes/archive/` (`git mv`, pour garder le fil).
6. Ajoute la ligne en tête de « Changements archivés » dans
   `changes/archive/JOURNAL.md`. Si le changement a défait quelque chose
   d'antérieur, ajoute aussi la ligne au tableau « essayé **et défait** ».
7. Mets `STATUS.md` à jour si l'état de marche du projet a bougé.
