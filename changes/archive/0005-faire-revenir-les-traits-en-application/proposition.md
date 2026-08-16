# Faire revenir un trait sous forme d'application, aussi souvent qu'un mot

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Mesuré sur un cours entier joué jusqu'au bout :

```
33 traits enseignés
niveau final ............ min 0, max 0
jamais redemandés ....... 33 / 33
```

Contre une moyenne de **4,5** pour les mots. Zéro ne veut pas dire « mal
appris » : ça veut dire **jamais revu une seule fois**.

La cause tient en une ligne, dans `_recall_targets` :

```python
exclude |= {i.name for i in seen_items if i.kind == "feature"}
```

**Cette ligne est juste.** On ne peut pas demander « c'était quoi, le mot pour
*pas de pluriel* ? ». Personne ne récite une règle. Ce qui est faux est la
conclusion qu'on en a tirée — *« donc il n'y a rien à faire »*. On ne peut pas
**redemander** un trait ; on peut le **réappliquer**.

Aujourd'hui, l'exposition totale d'un trait sur toute la vie du cours est : un
énoncé, une application. Puis le plan passe à l'item suivant et il ne reparaît
dans aucune leçon. C'est **un cinquième de ce qui est enseigné** — 35 items sur
170 — et un apprenant l'a rapporté dans ces termes : *« je n'ai rien compris à
la règle, et elle n'est même pas utilisée »*.

**Ce que ça ne coûte pas.** Un tour d'application n'est pas pris au vocabulaire :
13c épingle la phrase qui partage le plus de pièces avec le trait, et
l'instruction restreint la production aux mots déjà enseignés. La phrase produite
est donc faite de mots dus à révision. Un tour, deux bénéfices.

## Ce qui change dans SPEC.md

**Nouvelle règle — un trait revient, sous forme d'application.**
**Où :** code. Un trait `discrete` entre dans le tirage des rappels au même titre
qu'un mot, pondéré par le même niveau. Quand le tirage tombe sur lui, l'étape
émise est une **application** (13c) et non un rappel sec, parce qu'il n'y a rien
à réciter.

**Règle 17 — modifiée.** Elle décrit ce que les rappels de clôture excluent.
Elle devra dire que les traits `discrete` y entrent désormais, et que les
`strand` en restent exclus.

**Au passage, une garantie non écrite.** L'exclusion actuelle des traits du
tirage n'est documentée nulle part dans `SPEC.md` — l'audit ne l'avait pas
attrapée. Elle disparaît avec ce changement, mais il faut noter qu'elle
existait sans règle.

## Périmètre

**Dedans :**

- les traits `discrete` entrent dans le tirage de `_recall_targets`
- quand une cible tirée est un trait, `build_plan` émet une application au lieu
  d'un `rapidfire`
- l'exposition est enregistrée sur cette étape, pour que le niveau monte

**Dehors :**

- **les `strand`.** Ils se déclenchent depuis la matière — un mot a un jumeau de
  ton, une phrase contient une personne — et n'ont rien à faire dans un tirage.
  Ils restent exclus.
- **le niveau des mots employés dans la phrase.** L'application les exerce, mais
  le code n'enregistre rien pour eux : `record_recall` n'est appelé que là où il
  a demandé un mot précis et peut comparer la réponse. Élargir le niveau à « le
  mot était quelque part dans une phrase » lui ferait dire deux choses à la fois.
  Les mots gardent leur calendrier ; l'application est un bonus non compté.
- **tout jugement par le modèle.** Voir ci-dessous.

## La décision qui structure le reste

**Le niveau doit monter, et ce n'est pas optionnel.** Le tirage est pondéré par
le niveau, et la courbe est raide :

| niveau | tiré 1 fois sur… |
| --- | --- |
| 0 | 1 |
| 2 | 5 |
| 4 | 11 |
| 8 | 27 |

Un item à 0 est **treize fois** plus probable qu'un mot consolidé à 4,5. Si les
28 traits entrent dans le tirage et restent à 0 — ce qu'ils font aujourd'hui,
rien ne faisant monter leur niveau — ils ne seront pas « autant répétés que les
mots » : **ils écraseront tout le reste, en permanence.**

**Donc : compter l'exposition, sans juger.** Le niveau monte à chaque
application, qu'elle ait été réussie ou non.

L'alternative serait de faire juger le modèle, puisqu'une application demande une
phrase entière et n'offre aucune cible à comparer. Elle est écartée : ce serait
rendre au modèle une décision que ce projet a passé des semaines à ramener dans
le code, et pour un gain de fidélité qu'aucune mesure ne réclame.

## À trancher avant d'implémenter

**Faut-il plafonner à une application par item ?** Les rappels de clôture sont
tirés par paquets de 1 à 4. Si deux ou trois tombent sur des traits, la clôture
d'un mot devient deux ou trois productions de phrases d'affilée — long, et d'un
tout autre rythme qu'une série de rappels secs.

Deux réponses possibles : plafonner à une application par item, ou laisser le
tirage décider et regarder ce que ça donne en simulation. **Tranché : plafonné à une.**, quitte à relever le plafond après mesure — c'est le sens de
la règle 17, qui module déjà le nombre selon ce que l'item vient de faire dire.

## Tâches

- [x] Retirer l'exclusion des `discrete` dans `_recall_targets`, garder celle des `strand`
- [x] Émettre une application quand la cible tirée est un trait
- [x] Enregistrer l'exposition sur cette étape
- [x] Plafonner à une application par item, si c'est la décision retenue
- [x] Écrire la nouvelle règle dans `SPEC.md`, et modifier la 17
- [x] `python smoke_test.py`
- [x] `python simulate_progress.py` avant / après, et comparer les distributions

## Vérification

`simulate_progress.py` rejoue le vrai séquencement — `pick_next_index` choisit,
`build_plan` construit, `record_recall` note — donc il produit un état auquel le
tuteur aurait pu arriver. C'est l'outil qui a mesuré le 33/33 ; c'est lui qui
doit montrer que le chiffre a bougé.

**Ce que la vérification doit montrer :**

1. le niveau final des traits n'est plus 0, et se rapproche de celui des mots
   — c'est l'objectif littéral : « autant répété qu'un simple mot »
2. la distribution des tirages n'est pas dominée par les traits — vérifier qu'un
   mot consolidé n'a pas cessé d'être tiré
3. `smoke_test.py` passe, et une leçon ne se termine pas sur trois productions de
   phrases d'affilée

## Résultat

**Terminé le :** 2026-08-15.

| | traits | mots |
| --- | --- | --- |
| avant | tous à **1** — la seule exposition est l'introduction | médiane 5 |
| après | médiane **4**, de 0 à 8 | médiane 4 |

**L'objectif est atteint au sens littéral :** un trait est désormais aussi
travaillé qu'un mot. Le prix est visible et assumé — les mots passent de 5 à 4,
puisqu'ils partagent maintenant les créneaux.

Plafond vérifié sur 400 clôtures : **jamais deux applications**, jamais deux
d'affilée. 58 % des clôtures en portent une.

## Ce que l'implémentation a fait apparaître

**Une troisième barrière que la proposition n'avait pas vue.** L'exclusion des
traits n'était pas seule : `askable()` les rejetait aussi, et sa docstring disait
déjà pourquoi — *« teachable and askable are different: such an item can still be
TAUGHT, it just cannot be the bare question of a recall slot »*. C'est juste. Il
manquait un troisième mot : **`drawable`**, « peut occuper un créneau, sous une
forme ou une autre ». Les trois sont maintenant nommés côte à côte dans la
docstring de `drawable`, parce que c'est leur confusion qui a coûté le 33/33.

**Le champ `nature` n'était pas chargé.** `0001` l'avait écrit dans les 35 items,
mais le chargeur de `content.py` prend ses champs un par un et ignorait celui-là.
Le code ne pouvait donc pas distinguer `discrete` de `strand` — la donnée était
là, invisible. Ajoutée au dataclass et au chargement.

**La règle de notation était dupliquée**, et la copie a dérivé le jour même.
`simulate_progress.py` portait sa propre liste `("recall_piece", "rapidfire",
"settle")` sous un commentaire disant « exactement comme la boucle réelle ».
C'est l'outil qui a produit la mesure du 33/33 : laissé tel quel, il aurait
continué à rapporter « traits à 0 » **après** la correction. Rebranché sur
`RECALL_KINDS`, plus une branche pour les applications.

**Une extraction rendue nécessaire.** Le choix de la matière d'une application —
la construction épinglée, sinon les mots propres du trait, sinon la liste des
phrases connues — vivait dans la branche d'introduction. Les deux tours en ont
besoin, et c'est la même décision : extraite dans `_apply_material`. Les deux
tours formulent différemment (l'un peut dire « ces mots-là », que l'apprenant
vient de redire ; l'autre doit nommer sa propre matière) mais choisissent
pareil.

## Et la copie n'était pas seule

Après coup, une recherche des invariants recopiés en a trouvé **trois autres**,
dont **deux dans le fichier qu'on venait de corriger** : `simulate_progress.py`
écrivait la liste à trois endroits, `smoke_test.py` à un quatrième. J'avais
réparé l'instance sur laquelle j'avais trébuché, pas la classe.

Les quatre renvoient maintenant à `SCORING_KINDS`, défini une fois dans
`tutor.py` avec la raison écrite à côté. La seule occurrence littérale qui
subsiste est la définition.

**C'est la leçon la plus utile du lot** : trouver une prose périmée ne dit rien
sur le nombre de ses jumelles. Ce qui les trouve n'est pas l'attention, c'est une
recherche — et elle est mécanique, donc reproductible.
