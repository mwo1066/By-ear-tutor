# Trois endroits où le code disait quelque chose de faux

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Trois défauts sans rapport entre eux, réunis parce qu'ils ont la même forme :
**une phrase du programme qui ne correspond plus à ce qu'il fait.** Aucun n'est
un bug de comportement ; tous les trois trompent celui qui lit.

## Ce qui change dans SPEC.md

Une seule ligne, celle de la règle 17.

## 1. « Progress saved » quand rien n'est sauvé

Le message de fin lisait la constante `STATE_PATH` au lieu de demander au store
ce qu'il avait fait. Sous `--fresh`, `ProgressStore` n'a pas de chemin et sort
immédiatement de `save()` — mais la session annonçait quand même une sauvegarde.

La règle 32 dit « `--fresh` n'écrit rien du tout » : le comportement était juste,
c'est le message qui mentait. Et c'est **la seule ligne de la séance que
l'apprenant n'a aucun moyen de vérifier** — un fichier qu'il n'ouvrira pas.

Corrigé en demandant `store.path`.

## 2. Un trait sans glose n'était signalé nulle part

`check_roster` exemptait les traits du contrôle de glose. C'était **vrai quand
ça a été écrit**, le 9 août : le tour d'un trait était rédigé par le modèle, qui
pouvait travailler à partir de `description`. Le 11 août, le code s'est mis à
composer les questions à partir de la glose et de rien d'autre, et l'exemption a
survécu au changement qui la rendait fausse.

**La docstring de `_ask_for` promettait déjà la moitié manquante :** *« a missing
gloss falls back to the item's own notes instead AND IS REPORTED AT STARTUP »*.
Le repli marchait ; le signalement, non.

Ce n'est donc pas le repli qui a été retiré — il est délibéré, et son alternative
était pire (utiliser le nom vietnamien, c'est-à-dire une question qui donne sa
réponse). C'est le signalement qui a été rétabli.

**Signalé à part, et un par un.** Un *mot* sans glose est tenu hors des leçons et
compté en une ligne — ils sont 1 915, les lister noierait tout le reste. Un
*trait* sans glose est **quand même enseigné**, avec une question dégradée : ce
n'est pas le même problème, il est nommé item par item.

Mesuré avant d'écrire : 0 trait concerné aujourd'hui, donc zéro faux positif et
zéro leçon changée. C'est une garde pour le prochain trait écrit, pas une
correction du cours actuel.

**Laissé en place :** la seconde exemption, celle du contrôle « le nom apparaît
dans sa propre glose ». Pour un trait, mettre le mot vietnamien dans la glose est
**voulu** — c'est le commit `84c2104`. Retirer cette exemption-là entrerait en
conflit avec une pratique délibérée.

## 3. La glose d'une construction énonçait de la grammaire

`không phải là + [danh từ]` portait `gloss = "not be + [noun]"`, prononcé
**« not be something »**. La règle 10 dit qu'une glose est dite telle quelle et
n'est jamais une description grammaticale ; celle-ci était les deux à la fois.
`STATUS.md` le signalait depuis des jours.

- glose : `"not be + [noun]"` → `"I am not a ___"`, sur le modèle de
  `"My name is ___"` et `"I am ___ years old"` déjà en place
- littéral : `"not be + [noun]"` → `"not right is [noun]"`, qui est le vrai
  mot-à-mot de `không phải là` (`không` pas, `phải` juste, `là` est) au lieu
  d'une étiquette

**Jugement assumé, facile à défaire.** C'est du matériel de cours : si la
formulation ne convient pas, elle se change en une ligne dans le TOML.

**Pas touché :** `muốn + [động từ]` → `"want ___"`, que `STATUS.md` range dans le
même lot. Prononcé « want something », ce n'est pas une étiquette grammaticale —
c'est de l'anglais maigre. En inventer une meilleure sans mesure serait une
préférence, pas une correction.

## Et un quatrième, trouvé en écrivant

`N_RAPIDFIRE = 3` documentait la moyenne mesurée sur le cours de référence, et
ne servait plus à rien : `rapidfire_count` écrivait `3` en dur trois lignes plus
bas, et la constante ne restait que comme défaut d'un paramètre que seul le
smoke test emprunte. La règle 17 avait dû ajouter un avertissement — « **pas**
`N_RAPIDFIRE` » — pour éviter qu'on la modifie en croyant changer quelque chose.

**Rebranchée plutôt que supprimée.** La base du mot isolé *est* la moyenne
mesurée ; les deux autres se déduisent de ce que l'item vient de faire dire. La
constante dit maintenant ce qu'elle prétend dire, et l'avertissement de la règle
17 a disparu avec sa raison d'être.

Distribution vérifiée inchangée : 2–4 pour un mot, 1–2 pour une construction,
1–3 pour un trait.

## Périmètre

**Dedans :** `tutor.py` (le message de fin, `rapidfire_count`), `content.py`
(le contrôle de glose), un item de `02_xung_ho.toml`, la ligne **Changer** de la
règle 17.

**Dehors :** le repli sur `description` lui-même ; la seconde exemption de
`check_roster` ; la glose de `muốn + [động từ]`.

## Tâches

- [x] Lire `store.path` au lieu de `STATE_PATH` pour le message de fin
- [x] Signaler un trait sans glose, avec son propre message
- [x] Vérifier zéro faux positif sur le roster réel, et que la garde se déclenche
- [x] Réécrire la glose et le littéral de `không phải là + [danh từ]`
- [x] Rebrancher `N_RAPIDFIRE` sur la base du mot isolé
- [x] Corriger la ligne **Changer** de la règle 17
- [x] `python smoke_test.py`

## Vérification

`smoke_test.py` passe après chaque étape. Les deux branches du message de fin
testées séparément. La garde de glose testée sur un trait injecté sans glose, et
sur le roster réel : 1 915 problèmes, tous du stock muet, zéro trait.

## Résultat

**Terminé le :** 2026-08-15.

**Les quatre défauts ont la même forme**, et ce n'est visible qu'en les mettant
côte à côte : un message qui lit une constante au lieu de l'état, une exemption
vraie à l'écriture et fausse deux jours plus tard, une glose qui décrit au lieu
de dire, une constante qui documente une valeur qu'elle ne pilote plus. Aucun ne
casse une leçon. Tous les quatre trompent celui qui lit le code ou le contenu
pour décider quoi faire ensuite — c'est-à-dire nous, tout au long de la journée.
