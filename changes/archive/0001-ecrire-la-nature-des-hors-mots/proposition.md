# Écrire la nature et le tier de chaque hors-mot dans les items

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi
Le code traite les 35 hors-mots à l'identique — un `kind = "rule"`, une position,
enseigné, terminé. Or ils sont de deux natures : des **faits ponctuels** qui
s'enseignent une fois, et des **fils continus** qui s'attachent à toute la
matière (les tons à chaque mot, l'adresse à chaque phrase avec une personne).

La distinction avait été établie et mesurée le 15 août au matin, puis perdue :
elle n'existait que dans un transcript de conversation. Retrouvée par fouille, et
elle ne survivra que si elle est dans les fichiers.

**La mesure qui la motive :** 33 hors-mots enseignés sur tout le cours, niveau
final min 0 / max 0, jamais redemandés 33/33 — contre 4,5 de moyenne pour les
mots. Le code ne peut pas réparer ça tant qu'il ne sait pas distinguer un fait
d'un fil.

## Ce qui change dans SPEC.md
**Rien.** Aucun comportement ne bouge : les champs sont écrits, personne ne les
lit encore. La règle viendra avec le changement qui les utilise.

## Périmètre
**Dedans :** `nature` (`A`/`B`) sur les 35 hors-mots, `tier` (1/2/3) sur les 28
de nature A.
**Dehors :** toute lecture du champ par le code. Tout retrait des items de
catégorie B qui doublonnent un fil déjà en place — Meo ne s'est pas encore penché
sur la catégorie B, elle reste telle quelle.

## Tâches
- [x] Écrire `nature` et `tier` dans les huit fichiers de contenu
- [x] Vérifier que tous les TOML parsent encore
- [x] Vérifier la répartition : 7 / 11 / 10 en A, 7 en B
- [x] `python smoke_test.py`

## Vérification
`smoke_test.py` charge le cours entier et joue une séance : il passe. Le
chargeur choisit ses champs un par un et ignore les inconnus, donc les deux
nouveaux sont inertes par construction.

## Résultat
**Terminé le :** 2026-08-15 — 63 lignes ajoutées, 0 supprimée, 8 fichiers.

Fait sans passer par l'étape de proposition : c'est du report de décision, pas
une décision. La table de rattachement existait déjà dans `STYLE.md`, il n'y
avait rien à trancher.

**Deux items rattachés en cours de route.** `đang` et `sẽ` n'étaient dans aucune
catégorie — créés le 14 août par « Split the three tense markers into three
rules », donc avant la classification, qui les avait oubliés. Rangés en A tier 2
par Meo, à côté de `đã`, `rồi` et `chưa`. Le tier 2 compte 11 règles, pas 9.

**Une erreur corrigée avant d'écrire.** La session du matin donnait le fil de la
composition (« coller deux mots connus ») comme existant, via le `hook`. Mesuré :
`pieces` vaut 0 sur 2042 atomes et un seul atome porte un `hook`. Deux items de
catégorie B n'ont donc aucun fil — les nombres (rien nulle part) et la
composition (bloquée par du contenu à écrire, pas par du code).
