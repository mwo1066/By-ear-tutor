---
description: Relire le code et lister ce que SPEC.md affirme et qu'il ne fait plus
---

**Tu ne changes rien.** Le livrable est un rapport de dérive.

1. Lis `SPEC.md` en entier.
2. Pour chaque règle, va vérifier dans le code ce qu'elle annonce — en
   particulier les symboles nommés à la ligne **Changer :**. Une règle dont le
   symbole n'existe plus est une dérive, même si le comportement tient encore
   ailleurs.
3. Classe ce que tu trouves :
   - **Faux** — la règle affirme un comportement que le code ne produit plus.
   - **Déplacé** — la règle est juste, mais la ligne **Où :** dit code alors
     que c'est le prompt, ou l'inverse. C'est la dérive qui coûte le plus cher :
     une garantie annoncée qui n'est qu'une consigne.
   - **Périmé** — les fichiers ou symboles de **Changer :** n'existent plus.
   - **Absent** — le code garantit un comportement que `SPEC.md` ne mentionne
     nulle part.
4. Rapporte par numéro de règle, avec le fichier et la ligne, le plus grave en
   premier. Pas de correction : chaque dérive est soit une correction évidente à
   faire tout de suite sur demande, soit une proposition à ouvrir avec
   `/proposer`. Dis laquelle des deux, pour chacune.
