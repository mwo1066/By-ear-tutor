# Regrouper `SPEC.md` par sorte d'item, et aligner tout le vocabulaire sur le lexique

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Trois défauts de lisibilité, tous constatés en essayant de faire lire le projet
à quelqu'un d'extérieur.

**`SPEC.md` avait une section de 14 règles** — « Ce qui est enseigné, et dans
quel ordre » — qui mêlait quatre sujets sans rapport : l'ordre du cours, les
données que porte un item, l'enseignement d'un mot, celui d'une construction.
Et une section « Les hors-mots » séparée, alors qu'elle traite exactement la
même question pour la troisième sorte d'item. 59 règles sans sommaire.

**Le vocabulaire divergeait entre les fichiers.** `LEXIQUE.md` et le code
disaient `feature` depuis 0002 ; `SPEC.md` disait « hors-mot » 23 fois, et six
symboles du code portaient encore `RULE` dans leur nom.

**Et des garanties du contenu restaient non écrites** — la suite de l'audit
commencé en 9b/9c/11c.

## Ce qui change dans SPEC.md

**Aucun texte de règle n'est réécrit.** Ce sont des titres de section, un ordre
de blocs, un sommaire, et deux paragraphes ajoutés à la règle 10.

Le bloc central se scinde en cinq sections, dont les trois dernières suivent les
trois sortes d'item du lexique, dans l'ordre :

| section | règles |
| --- | --- |
| L'ordre du cours | 8, 9, 9b, 9c |
| Ce que le cours sait | 10, 10b |
| Enseigner un mot | 11, 11b, 11c |
| Enseigner une construction | 12, 12b, 12c, 12d, 13 |
| Enseigner un trait | 13b, 13c, 13d |

**Un seul renumérotage :** `12e` devient `10b`. Le profil de l'apprenant rejoint
« chaque item porte ses propres données » — l'une dit ce que le cours sait des
items, l'autre ce qu'il sait de l'apprenant. Laissé où il était, il coupait la
section des constructions en deux.

**Le sommaire pose la convention** qui évitera la question la prochaine fois :
les numéros de règle sont des **identifiants stables**, ils ne se renumérotent
pas quand une section bouge. C'est ce qui permet de réorganiser sans invalider
les renvois de `STYLE.md`, du `LEXIQUE.md` et des commentaires du code.

**Deux ajouts à la règle 10**, tirés de l'audit du contenu :

- **le repli sur `description`** — sans gloss, deux endroits retombent sur les
  notes d'écriture, rédigées en vietnamien. Aucun item enseigné n'a de gloss
  vide, donc rien ne le déclenche ; mais c'est la forme latente du défaut que
  `a6f5021` a corrigé dans `_lesson_note`, où des fragments de vietnamien
  ressortaient au milieu de phrases anglaises.
- **les champs inertes** — `type` sur les 2085 items, `senses` et
  `frequency_rank` sur les 1915 du stock. Aucun ne pilote une décision.

## Périmètre

**Dedans :** la structure et le sommaire de `SPEC.md` ; « hors-mot » → « trait »
dans `SPEC.md` et `STYLE.md` ; les six symboles du code portant `RULE` ; les
commentaires de `content.py` décrivant encore le type `rule` ; les deux
paragraphes de la règle 10.

**Dehors :**

- **le texte des règles.** Aucune n'est réécrite : ce changement doit pouvoir se
  relire comme un déplacement, pas comme une révision.
- **`Rule 9` dans un commentaire de `tutor.py`** — celui-là désigne bien une
  règle de `SPEC.md`. C'est l'usage correct du mot, il reste.
- **`LEXIQUE.md`**, déjà aligné puisqu'il est la source.

## Ce qui revient sur une décision de 0002

`0002` avait **exclu explicitement** le renommage des symboles, au motif que les
lignes **Changer** de `SPEC.md` nomment des symboles et qu'un renommage les
aurait toutes invalidées d'un coup.

C'était juste à ce moment-là. Ici les deux se font dans le même passage : les
symboles et les lignes qui les nomment changent ensemble, donc l'argument tombe.
Six noms concernés — `MAX_RULE_PIECE_RECALLS`, `MIN_ITEMS_BETWEEN_RULES`,
`_rule_is_due`, `rules_due`, `first_rule`,
`check_rule_glosses_name_their_word` — c'est-à-dire peu, ce qu'on ne savait pas
avant de compter.

## Tâches

- [x] Déplacer le bloc `12e` et le renuméroter `10b`
- [x] Scinder le bloc central en cinq sections
- [x] Renommer « Les hors-mots » en « Enseigner un trait »
- [x] Écrire le sommaire, avec la convention sur les numéros stables
- [x] « hors-mot » → « trait » dans `SPEC.md` et `STYLE.md`
- [x] Renommer les six symboles, et les lignes **Changer** qui les nomment
- [x] Aligner les commentaires de `content.py`
- [x] Ajouter le repli `description` et les champs inertes à la règle 10
- [x] `python smoke_test.py` après chaque étape

## Vérification

`smoke_test.py` passe après chacune des quatre étapes. Zéro occurrence de
« hors-mot » dans les trois documents, zéro symbole contenant `rule` hors des
mentions en prose qui désignent une règle de `SPEC.md`. 59 règles avant, 59
après.

## Résultat

**Terminé le :** 2026-08-15 — commit `a1f3285`, six fichiers : `SPEC.md`,
`STATUS.md`, `STYLE.md`, `content.py`, `tutor.py`, `smoke_test.py`.

**Ce dossier a été écrit après le commit, pas avant.** Le changement a été
commité tel quel, avec un message d'une ligne — « Cleanup spec, align with
content and add section » — qui ne dit ni le renumérotage de `12e` en `10b`, ni
la convention sur les numéros stables, ni le retour sur l'exclusion posée par
`0002`. Comme `a1f3285` était déjà poussé, le message n'a pas été réécrit :
c'est ce dossier qui porte le détail, et le commit suivant y renvoie.

C'est exactement le cas que le rituel doit rendre visible plutôt qu'empêcher. Il
n'empêche rien — il laisse une trace quand on le saute, et la trace ici est un
dossier daté d'après son commit.

**Le sommaire n'était pas demandé** et c'est probablement l'apport le plus utile
du lot : 59 règles sans table des matières se parcourent mal, quel que soit leur
regroupement.

**Une trouvaille du tri des champs de contenu.** La recherche initiale donnait
`description` lu 29 fois et `type` 31 fois dans le code, ce qui suggérait deux
mécanismes non documentés. En réalité la quasi-totalité de ces occurrences sont
des clés de schéma JSON pour la définition des outils, sans rapport avec les
champs d'un item. Compter des occurrences ne dit pas ce qu'elles font — il a
fallu regarder chacune. Le vrai usage tient en trois lignes, et une seule
méritait d'être écrite.
