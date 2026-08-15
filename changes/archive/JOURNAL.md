# Journal des changements

La liste de ce qui a été fait, la plus récente en haut. **À lire avant de
proposer quoi que ce soit** — c'est ici qu'on voit si l'idée a déjà été
essayée, et ce qu'elle avait donné.

Une ligne par changement archivé, au format :

`NNNN — <titre> — AAAA-MM-JJ — <ce que ça a donné en une phrase>`

---

## Changements archivés

`0003` — **regrouper `SPEC.md` par sorte d'item, et aligner tout le vocabulaire**
— 2026-08-15 — le bloc central de 14 règles se scinde en cinq sections, dont trois
« Enseigner un… » qui suivent les trois sortes d'item du lexique. Sommaire ajouté,
et la convention posée : **les numéros de règle sont des identifiants stables**,
ils ne se renumérotent pas quand une section bouge. « hors-mot » → « trait »
partout, et les six symboles portant `RULE` renommés — ce qui **revient sur une
exclusion explicite de 0002**, dont l'argument tombe dès lors que les symboles et
les lignes **Changer** changent ensemble. Aucun texte de règle réécrit. Livré par
le commit `a1f3285`, dont le message d'une ligne ne dit presque rien du
changement — le dossier a été écrit après coup, et c'est lui qui porte le détail.

`0002` — **nommer les hors-mots `feature`, et leurs natures `discrete` / `strand`**
— 2026-08-15 — supprime la collision entre « règle » le comportement et « règle »
l'item enseigné, qui avait fait perdre le fil deux fois dans la même séance.
`feature` au sens de la typologie linguistique — la plupart des 35 sont des
traits nommés de l'atlas WALS. A produit `LEXIQUE.md`, 28 termes groupés selon
qu'ils viennent du domaine, en sont une restriction, ou ont été inventés ici.
Valeurs seulement : aucun nom de symbole n'a bougé, donc les lignes **Changer**
de `SPEC.md` restent valides.

`0001` — **écrire la nature et le tier de chaque hors-mot dans les items** —
*(les valeurs s'appelaient `A` et `B` ; renommées `discrete` et `strand` par 0002)* —
2026-08-15 — 35 items annotés (28 faits ponctuels répartis sur trois tiers, 7 fils
continus), zéro
comportement changé. Rend possible le retour des applications sur les faits
ponctuels. A rattrapé deux oublis de la classification du matin :
`đang` et `sẽ`, rangés en tier 2 par Meo et écrits comme les 33 autres. Et
corrigé une erreur : le fil de la composition n'existe pas, contrairement à ce
qui avait été conclu.

---

# Avant le rituel

Les 123 commits d'avant ce journal. Reconstitué depuis `git log`, donc fidèle
aux titres de commits et à rien d'autre : ce qui a été fait est exact, le
« pourquoi » n'y est que là où le commit le disait.

Pour retrouver le détail d'une ligne : `git show <hash>`.

## Ce qu'on a déjà essayé **et défait**

Ce sont les entrées les plus utiles du fichier : chacune est une chose qui
paraît une bonne idée, qu'on a implémentée, et qu'on a retirée. Elles sont
celles qu'on redemande sans le savoir.

| l'idée | essayée | défaite | où ça a atterri |
| --- | --- | --- | --- |
| **Réparer les transcriptions approximatives** après coup | `accec85` 2026-07-27 | `35b4caa` le même jour — laisser le tuteur juger l'écart | `SPEC.md` règle 26 : « La transcription n'est jamais réparée » |
| **Un modèle de secours** en cas de panne du principal | `2e274e3` 2026-07-21, puis `62af20c` (retour à llama-3.1-8b, gpt-oss-20b cassait les appels d'outils) | `31543a7` 2026-07-27 — attendre le vrai modèle | `SPEC.md` règle 30 : « Un seul modèle, aucun secours » |
| **Abandonner les tons** | supprimés `e46cbe2` 2026-07-27 | remis `29f7ffb` 2026-08-14, une paire dite à voix haute quand le second des deux est enseigné | `SPEC.md` règle 28b : « Les tons SONT enseignés » — mais règle 28 : jamais de jugement sur la prononciation |
| **Le push-to-talk** | `92f0ccf` 2026-07-22 | remplacé par les mains libres, détecteur + volume `c3018e2` 2026-08-09 | `SPEC.md` règles 23, 23b |
| **Le projet en anglais** | `6a78dd1` 2026-08-07 | `SPEC.md` réécrit en français `159ea0b` 2026-08-09 | code et prompts en anglais, docs que tu lis en français |
| **Un outil `next_item`** confié au modèle | avant `216637e` | `216637e` 2026-07-28 — la séquence voyage dans le contexte | `SPEC.md` règles 8, 29 |
| **Le correcteur de fin de séance** | avant `c2e15ae` | `c2e15ae` 2026-07-29 | remplacé par le niveau par mot, règle 14 |

## Le motif qui revient le plus souvent

**Le prompt grossit, puis il faut le vider.** Quatre fois :

- `17c8406` 2026-07-27 — consolidation, 3742 → 2703 tokens à règles égales
- `473df0d` 2026-07-28 — « défaire le gonflement du prompt depuis la consolidation »
- `77bdffc` 2026-07-28 — retirer les règles décrivant des situations que le code empêche déjà
- `4987b96` 2026-07-28 — supprimer les règles mnémotechniques et de récit

C'est ce motif qui a produit la ligne **Où : code / prompt** en tête de
`SPEC.md`. Toute proposition qui ajoute au prompt doit dire ce qu'elle en
retire, ou pourquoi le code ne peut pas le faire.

**Le discours d'ouverture, quatre fois aussi :** raccourci `2bc148a`, empêché
d'être écrasé `202aef5`, restauré `4fc4cc8` (un plan vide voulait dire deux
choses opposées), réécrit autour des trois points de Meo `b14f73c`. Atterri en
règle 27.

## Les étapes structurantes

| quand | ce qui a changé | commits |
| --- | --- | --- |
| 2026-07-21 | premier cerveau de tuteur, texte seul | `81f02b1` |
| 2026-07-22 | les deux voix, première conversation parlée | `aa3d7c6`, `6075851`, `5802d86` |
| 2026-07-27 | la boucle refondue sur la méthode réelle de Paul Noble | `f6cb2bb` |
| 2026-07-29 | **le cycle d'enseignement devient une machine à états en code** | `ae0b608`, `c2e15ae` |
| 2026-08-09 | naissance de `SPEC.md` | `0da69a0`, `159ea0b` |
| 2026-08-11 | **le code écrit les tours mécaniques**, sans appel au modèle | `7e7728c` (décision), `bf69808` (fait) |
| 2026-08-11 | naissance de `STYLE.md`, le carnet d'idées | `d2d994f` |
| 2026-08-12 → 08-13 | le contenu se complète : personnes, questions, nombres, modaux, lieux | `f3e7e14`, `3cf528f`, `bd53620`, `a386650` |
| 2026-08-14 → 08-15 | les règles deviennent enseignables : une règle nomme ses mots, le code choisit la phrase, on demande les mots un à un puis on assemble | `5560fd7`, `9506a3d`, `b40d766`, `bb45efc` |

## Où chercher le reste

`git log --oneline` donne les 123 titres. Ils sont écrits pour être lus : le
titre dit ce que le commit change, pas quel fichier il touche.

Recherche par sujet :

```bash
git log --oneline --grep=rule
```
