# Comment le tuteur parle — carnet d'idées

**Ce fichier n'est lu par personne à l'exécution.** Ni le tuteur, ni le code, ni
le modèle. C'est un carnet : les idées atterrissent ici, et chacune en sort par
un des trois tiroirs ci-dessous, ou n'en sort pas.

Une liste de style que l'IA consulterait pendant la leçon serait le prompt avec
des étapes en plus — elle grossirait, se contredirait, et le modèle en
ignorerait une partie. C'est exactement ce qu'on a passé une journée à défaire.

---

## Les trois tiroirs

| l'idée porte sur… | elle va… | exemples déjà en place |
| --- | --- | --- |
| **un mot précis** | un champ sur l'item | `hook` (« Vietnam is the second biggest coffee grower… ») |
| **un geste qui revient** | une formulation en code | `_REPEAT_ASK`, `_ACK_CORRECT`, `_INTRODUCE` |
| **la manière d'être** | le prompt, en dernier recours et à la place d'autre chose | THE CORE MOVE, THREE RULES |

## Le test avant d'ouvrir un tiroir

**Combien de fois ça apparaît dans le cours de référence ?**

C'est ce qui a rendu le mouvement central solide : *« repeat after me »* zéro
fois en vingt-cinq minutes, *« how would you say »* vingt-deux fois. Pareil pour
*« and again, what was ___ ? »*, vingt et une occurrences — devenu `_REPEAT_ASK`.

Une idée qu'on ne peut pas compter dans la référence est une préférence. Une
préférence ne va dans aucun tiroir tant qu'elle n'a pas été mesurée. On peut
quand même l'essayer — mais alors on le sait, et on regarde ce que ça donne.

---

## Idées en attente

### Redire le mot juste après la réponse de l'apprenant
*Proposé par Meo.*

Après un rappel, l'apprenant répond, le tuteur confirme — et Minh redit le mot.
L'apprenant vient de le produire, il l'entend correct dans la seconde qui suit :
c'est le seul moment où la comparaison est immédiate.

**Tiroir :** geste qui revient → une formulation en code, dans
`_acknowledgement`. « That's it — tôi. » au lieu de « That's it. »

**Ce qui joue pour :** c'est la seule aide à la prononciation que ce cours peut
donner honnêtement. Le tuteur n'entend jamais l'apprenant (SPEC 28), donc il ne
peut pas corriger — mais il peut redonner le modèle. Et le mot vietnamien en fin
de phrase du tuteur est exactement la place que SPEC 3 lui réserve, donc un seul
changement de voix, pas deux.

**Ce qui joue contre :** un changement de voix coûte un aller-retour de
synthèse. Et il faut le garde-fou qui existe déjà pour `missed_twice` — si la
question suivante porte sur le même mot, le redire, c'est donner la réponse.

**Pas encore mesuré** dans le cours de référence. À compter : est-ce qu'il
répète le mot après une bonne réponse, ou est-ce qu'il enchaîne ?

**Statut :** à essayer.

### Décomposer un nom connu, pour en enseigner deux d'un coup
*Proposé par Meo.*

Quand un mot connu se découpe en mots qui existent, le dire. En chinois, Beijing
= nord + capitale. En vietnamien on a exactement les mêmes, parce qu'une grande
part du vocabulaire est composée :

```
sân bay     = sân (cour, terrain) + bay (voler)      un terrain où l'on vole
Hà Nội      = hà (fleuve) + nội (dedans)             dedans le fleuve
bánh mì     = bánh (galette) + mì (blé)
máy bay     = máy (machine) + bay (voler)
```

L'apprenant croit apprendre un mot, il en range deux — et le second lui reste
parce qu'il l'a rencontré dans quelque chose qu'il connaissait déjà.

**Tiroir :** un champ sur l'item → c'est exactement le `hook`, mais sa meilleure
forme. À écrire dans la consigne de la passe d'annotation, pas à laisser au
hasard.

**La condition qui compte :** les deux morceaux doivent être de vrais mots. Une
étymologie inventée prononcée à voix haute est pire que pas de hook du tout, et
un modèle en fabrique volontiers. La consigne dit déjà « ne devine jamais » ;
pour une décomposition il faut en plus que chaque partie soit vérifiable.

**Combien de mots sont concernés — mesuré le 11 août** sur les 2000 mots
importés par fréquence :

```
2000  mots
 874  composés de plusieurs syllabes                        43 %
 382  se découpent ENTIÈREMENT en mots eux-mêmes présents   1 mot sur 5
```

Ce n'est donc pas une curiosité à sortir trois fois dans le cours. Un mot sur
cinq peut s'enseigner comme ça, avec du vocabulaire que le cours contient déjà.

```
làm việc  = làm (faire) + việc (travail)     travailler
bắt đầu   = bắt (saisir) + đầu (tête)        commencer
xây dựng  = xây (bâtir) + dựng (dresser)     construire
Việt Nam  = Việt + Nam (sud)
```

**Et deux pièges que la même mesure a sortis.**

*Les fausses décompositions.* `bao giờ` (quand) se découpe mécaniquement en
`bao` (sac) + `giờ` (heure). Ça ne veut rien dire : c'est un autre morphème qui
s'écrit pareil. Un découpage automatique en produit, et rien dans les données ne
les distingue des vraies.

*Le sens des morceaux ne se lit pas dans le Wiktionary.* `thông tin` =
information ; Wiktionary donne `thông` = « river ». Le sens utile ici est 通,
« faire passer » — donc « faire passer une nouvelle ». Même défaut que `là` →
« fine silk » : le premier sens listé est l'archaïque.

**Donc : la structure est fréquente et vaut le coup, mais elle ne s'automatise
pas.** Le modèle doit juger chaque décomposition sous la contrainte « ne devine
jamais », et la qualité dépend du même travail que les glosses. Un découpage
mécanique produirait « sac-heure » à voix haute.

**Limite honnête :** ça marche sur les composés sino-vietnamiens, pas sur tout.
`phở` ne se décompose pas. C'est un type de hook, applicable là où il s'applique
— pas une règle à forcer partout.

**Piste, pas encore creusée :** si les morceaux sont de vrais mots, ils
pourraient devenir des items à part entière. `bay` mériterait sa place après
`sân bay` — l'apprenant le rencontrerait deux fois, une fois caché dans
« aéroport », une fois pour lui-même.

**Statut :** câblé dans `fill_item_metadata.py`, pas encore vérifié sur des
propositions réelles.

### Ne pas féliciter à chaque fois
*Observé pendant les séances du 11 août.*

`_ACK_CORRECT` place « That's it. / Exactly. / Good. » devant presque chaque
question. Sur une série de rappels ça fait quatre félicitations en quatre tours,
et ça finit par ne plus rien vouloir dire.

**Tiroir :** formulation en code — une chaîne vide dans le tirage, pour que
l'accusé de réception saute parfois.

**Statut :** à mesurer d'abord. Le cours de référence confirme-t-il chaque
bonne réponse, ou seulement les difficiles ?

### Le silence après la question
*Observé.*

La règle 2 du prompt dit que le tour s'arrête à la question. Elle tient. Mais
rien ne dit combien de temps on laisse. Aujourd'hui le micro s'ouvre dès que la
synthèse a fini de jouer.

**Tiroir :** ni prompt ni contenu — c'est `listen.py`.

**Statut :** pas un problème de style, rangé ici par erreur. À déplacer si ça
devient un vrai sujet.

---

## Déjà mesuré dans le cours de référence

Les faits qui ont servi jusqu'ici, gardés ensemble pour qu'on n'ait pas à les
remesurer :

- « repeat after me » : **0** fois en vingt-cinq minutes
- « how would you say ___ ? » : **22** fois → THE CORE MOVE
- « and again, what was ___ ? » : **21** fois → `_REPEAT_ASK`
- questions de rappel : environ **3 par mot nouveau** → `N_RAPIDFIRE`
- rien n'est jamais « acquis » puis retiré ; un mot revient de moins en moins
  → `srs.weight`, `DECAY`

Et sur le vocabulaire lui-même, mesuré sur la liste de fréquence :

- **43 %** des 2000 mots les plus fréquents sont polysyllabiques
- **1 sur 5** se découpe entièrement en mots présents dans la même liste

---

## Les notes de Meo

Attendues, pas encore intégrées. Quand elles arrivent : note par note, quel
tiroir — et lesquelles ne survivent pas au test.
