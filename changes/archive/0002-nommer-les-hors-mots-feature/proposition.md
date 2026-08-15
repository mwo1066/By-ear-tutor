# Nommer les hors-mots `feature`, et leurs natures `discrete` / `strand`

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Le mot « règle » désignait deux choses, et la collision a coûté du temps à
l'auteur du projet lui-même : au cours d'une seule séance, il a fallu s'arrêter
deux fois pour redémêler « une règle de `SPEC.md` » (un comportement du
programme) de « un item `kind = "rule"` » (un fait de vietnamien qu'on enseigne).

Un avis extérieur a posé le diagnostic complet : plusieurs termes ont été
inventés au fil des conversations, aucun n'est défini au même endroit, et rien
ne dit lesquels sont du vocabulaire du domaine et lesquels sont propres à
l'application. Le projet est illisible pour qui n'a pas assisté aux
conversations — ce qui, à terme, inclut son auteur.

**Et `A` / `B` n'aidait pas.** Deux lettres ne portent aucun sens : il faut la
table pour savoir laquelle veut dire quoi, à chaque lecture.

## Ce qui change dans SPEC.md

Aucune règle ajoutée ni supprimée. Trois corrections de vocabulaire :

- règle 13, la note — le type d'item ne s'appelle plus `rule`
- section « Les hors-mots », **Nom dans le code** — devient `kind = "feature"`,
  avec la justification WALS et les deux valeurs de `nature`
- règles 13b et 13c, ligne **Changer** — « la branche `rule` » devient « la
  branche `feature` »

**Où :** contenu et code, mais aucune garantie ne bouge. Ce sont des valeurs,
pas des mécanismes.

## Le choix du nom

`feature`, au sens de la **typologie linguistique**, et non « grammar point » :
ce cours range parmi ses hors-mots les tons et la politesse, qui ne sont pas de
la grammaire. La plupart des 35 correspondent à un trait nommé de l'atlas WALS —
81A *Order of Subject, Object and Verb*, 13A *Tone*, 55A *Numeral Classifiers*,
45A *Politeness Distinctions in Pronouns*.

`strand` vient de la conception de curriculum : un fil qui traverse tout un
programme sans jamais finir. `discrete` est son opposé naturel.

## Périmètre

**Dedans :** les **valeurs** `kind = "rule"` → `"feature"` et `nature = "A"/"B"`
→ `"discrete"/"strand"`, dans le contenu et dans le code ; les références
correspondantes dans `SPEC.md`, `STYLE.md` et `README.md` ; l'écriture de
`LEXIQUE.md`.

**Dehors :**

- **les noms de symboles** — `MAX_RULE_PIECE_RECALLS`, `MIN_ITEMS_BETWEEN_RULES`,
  `_rule_is_due`, `rules_due`. Les renommer aurait invalidé d'un coup les lignes
  **Changer** de `SPEC.md`, qui nomment des symboles. À faire séparément, si un
  jour ça vaut le coup.
- **le tour `rule`** — l'étape qui nomme le motif à la fin d'une construction.
  C'est une sorte de **tour**, pas une sorte d'**item** : une fois le type
  d'item renommé, il n'y a plus de recouvrement.

## Tâches

- [x] Renommer la valeur `kind` dans les 8 fichiers de contenu (35 items)
- [x] Renommer `nature` : `A` → `discrete`, `B` → `strand`
- [x] Renommer les 17 sites de code portant sur le `kind` d'un item
- [x] Laisser intacts les 4 sites portant sur le `kind` d'une **étape**
- [x] Corriger les références dans `SPEC.md` et `STYLE.md`
- [x] Écrire `LEXIQUE.md` en anglais, groupé par origine du terme
- [x] Ajouter la carte des documents au `README.md`
- [x] `python smoke_test.py`

## Vérification

`smoke_test.py` charge le cours entier et joue une séance complète : il passe.
La répartition est inchangée après renommage — 7 / 11 / 10 en `discrete`, 7 en
`strand`, 35 au total. Aucun `kind` d'item ne porte plus la valeur `rule`.

## Résultat

**Terminé le :** 2026-08-15 — 4 fichiers de code, 8 fichiers de contenu,
3 documents, plus `LEXIQUE.md` créé.

**Le lexique est en anglais alors que `SPEC.md` et `STYLE.md` sont en français.**
Assumé : ces deux-là sont lus par une personne, le lexique est ce qu'on tend à
quelqu'un d'extérieur. Le `README.md` le dit en une ligne.

**Les termes y sont groupés par origine**, ce qui est l'apport principal et ne
venait pas de la demande initiale : *standard* (13 termes du domaine, employés au
sens du domaine), *borrowed and narrowed* (7 mots standards restreints ici), et
*coined here* (8 sans équivalent). Un lecteur qui connaît la didactique des
langues sait immédiatement quelles définitions il peut sauter.

**Une collision de vocabulaire trouvée en écrivant :** `tier` est aussi le nom
d'une grille connue en enseignement du vocabulaire (Beck), qui range les mots par
utilité **académique**. Ici la grille classe par utilité **conversationnelle**.
Même mot, autre schéma — c'est écrit dans le lexique plutôt que renommé, parce
que `tier` reste le mot que Meo emploie.
