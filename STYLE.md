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

## 1. Ce qui tourne déjà dans le tuteur

Ces idées ne sont plus des idées : quelque chose du tuteur les exécute. **Deux
sont entières, trois ne couvrent qu'une partie** de ce qu'elles proposaient — et
pour celles-là, ce qui reste est nommé dans leur statut.

Une entrée qui arrive ici doit dire **où** elle vit : une règle de `SPEC.md`, un
symbole du code, ou un champ du contenu. Sans ça, personne ne saura l'an prochain
si elle tourne encore.

### Demander qui est l'apprenant, pour lui enseigner SES pronoms
*Proposé par Meo.*

→ Un **`strand`**, un fil continu — et l'item `cách chọn từ xưng hô` en est le
vestige. Voir « Les traits : deux natures, pas une ».

En vietnamien, le mot pour « je » dépend de qui parle à qui. Meo s'adressant à
sa copine dit `anh` pour « je » et `em` pour « tu ». Ce ne sont pas des
variantes exotiques : c'est ce qu'il dira tous les jours.

Le cours enseigne aujourd'hui `tôi`, et sa propre fiche dit pourquoi c'est
tiède :

> *« 'tôi' đúng ngữ pháp nhưng lạnh »* — grammaticalement juste, mais froid.

Puis il enseigne `anh`/`chị`/`em` dans l'abstrait, comme une règle à connaître.
Si le cours savait qui vous êtes, ce ne serait plus une règle — ce serait **vos**
mots.

**Ce que ça débloque, et ce n'est pas qu'un mot :**

- « je » devient `anh` ou `em` selon l'interlocuteur, au lieu du `tôi` neutre
- la règle `cách chọn từ xưng hô` cesse d'être un tableau à mémoriser et devient
  « pour vous, avec quelqu'un de plus jeune, vous êtes `anh` »
- les phrases deviennent vraies : « tôi tên là Mathias » au lieu d'un prénom
  inventé

**Tiroir :** aucun des trois — c'est un **profil d'apprenant**, une donnée
persistante qui n'existe pas encore. `state.json` ne connaît que des niveaux par
mot. STATUS le signale déjà pour le nom ; l'âge et le genre sont le même champ.

**Ce qu'il faut, au minimum :** une tranche d'âge et un genre. C'est ce qui
détermine si vous êtes `anh`, `chị` ou `em` face à quelqu'un.

**La limite honnête :** le système d'adresse dépend des DEUX personnes. Savoir
qui vous êtes est nécessaire, pas suffisant — il faut aussi savoir à qui vous
parlez. Mais le cours peut dire « avec quelqu'un de plus jeune, vous êtes
`anh` », ce qui est infiniment plus concret que la règle générale.

**Comment le demander :** le cours enseigne déjà `bạn tên là gì?` — « comment
tu t'appelles ? ». Il pose la question pour de vrai et garde la réponse. L'âge
a son item aussi (`Tôi ... tuổi`). Le cours contient donc déjà les questions qui
remplissent son propre profil.

**La preuve, tombée en séance le 11 août.** Meo demande : « est-ce que je peux
dire *Anh tên là* si je m'adresse à un mec plus vieux ? » Le tuteur n'a pas su
répondre ; la question est arrivée ici.

La réponse est non — face à un homme plus âgé, lui c'est `anh` et vous c'est
`em`. Et dans le log, Meo avait déjà tenté « An... An... An ten la... » : il
substituait le pronom tout seul, dans le mauvais sens. **La question à laquelle
le cours ne sait pas répondre est exactement celle que le profil rendrait
triviale.**

**Fait le 11 août, en attendant le profil :** une règle en position 2, juste
après `tôi` — *« le vietnamien change le mot pour "je" selon à qui on parle ;
vous les verrez bientôt, et tôi ne sera jamais faux en attendant »*. Elle ne
donne aucun tableau (les mots n'existent pas encore), elle empêche seulement de
construire l'habitude « tôi = I » qu'il faudra défaire à l'item 11.

**Statut : FAIT**, le 14 août — « Let the course know who the learner is, so it
can teach THEIR person-words ». Le profil vit dans `learner.py` et `learner.json`,
et `build_plan` le lit pour composer les situations d'adresse (SPEC 13d). Restait
vrai à l'écriture : c'était probablement la personnalisation la plus rentable de
toute la langue — le système d'adresse est ce qui distingue quelqu'un qui parle
vietnamien de quelqu'un qui récite du vietnamien.

### Les tons : donner un modèle, jamais un jugement
*Proposé par Meo, 13 août.*

→ Un **`strand`**, un fil continu. Voir « Les traits : deux natures, pas une ».

**Le mur qui décide de tout : le tuteur n'entend jamais la prononciation de
l'apprenant.** Pas de « c'était presque ça, remonte un peu ». Donc la seule
pédagogie disponible est de **rendre la différence audible** — donner un modèle
et créer un contraste, jamais évaluer.

Ce n'est pas une limite à contourner, c'est ce qui choisit le design.

**Les trois temps, dans l'ordre :**

1. **Dès les premières minutes** — « écoute Minh et copie ». Une consigne, dite
   une fois, vraie du début à la fin du cours. C'est la fondation.
2. **À l'introduction d'un mot** — nommer son ton, quand ce mot en a besoin.
   Jamais un tableau des six tons le premier jour : c'est la règle écrite dont
   ce cours ne veut pas.
3. **Quand un mot nouveau ressemble à un ancien déjà consolidé** — les comparer,
   dire les deux tons, et faire dire les deux par Minh dans le même souffle.

Le troisième temps est le seul moment où la différence existe vraiment pour
l'oreille. `ba` puis `bà`, un seul clip, deux mots.

**Combien de mots sont concernés — mesuré le 13 août :**

```
                                    enseignés (147)      tout (2062)
même squelette, TON différent         3 groupes      246 groupes / 582 mots
+ voyelle modifiée (ơ/o, ư/u, ê/e)    3 groupes      289 groupes / 801 mots
```

**Presque 40 % du vocabulaire a un sosie.** Mais trois paires seulement parmi
les mots enseignés : le mécanisme ne sert quasiment à rien aujourd'hui et
devient central quand le vocabulaire grossit. À écrire, pas à câbler tout de
suite.

Les trois qui existent :

```
ba  (ngang) trois          /  bà  (huyền) grand-mère
bạn (nặng)  toi            /  bán (sắc)   vendre
con (ngang) classificateur /  còn (huyền) et toi ?
```

**Tiroir :** geste qui revient → une formulation en code, dans `_INTRODUCE`.
Rien à annoter : le ton se **calcule** depuis le diacritique, comme les notes de
ton écrites aujourd'hui dans les fichiers de contenu.

**La condition qui compte : le second mot seulement.** Deux sosies enseignés
côte à côte s'entremêlent. La comparaison se déclenche à l'introduction du
NOUVEAU, et seulement si l'ancien est bien consolidé — le niveau SRS donne ce
chiffre. Le cours le fait déjà par accident : `bạn`/`bán` sont à 125 items
d'écart, `con`/`còn` à 105. Seul `ba`/`bà` est serré, à 15.

**Deux choses à ne pas faire.**

*Ne jamais valider un ton.* « Bien, c'était le bon ton » est une information
qu'on n'a pas. Une fausse confirmation installe l'erreur avec un tampon de
garantie — pire que le silence.

*Ne pas parler du ton d'un mot composé.* `cà phê` n'a pas un ton, il en a deux.
Les notes de ton sont par syllabe, ce que le calcul par diacritique donne déjà.

**Une réserve sur notre propre outil.** Minh est une voix de synthèse, et un mot
isolé ne porte pas son ton comme le même mot dans une phrase — l'intonation de
phrase déforme. Ce qui plaide pour le temps 1 : **le mot répété seul est la
référence propre**, et c'est ce qu'on a de plus fiable.

**Statut : FAIT au temps 3**, le 14 août — « Say a tone pair out loud when the
second of the two is taught ». Le calcul vit dans `tone_twin`, la paire est dite
par Minh dans `_INTRODUCE`, et SPEC 28b porte la règle. Les temps 1 et 2 restent
ouverts.

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

**La moitié qui existe déjà — SPEC 18c.** Le mot EST redonné, mais uniquement
quand l'apprenant s'est trompé : « It was ngon. » Sur une bonne réponse il reçoit
« That's it. », sans le mot. Ce qui est proposé ici est donc l'**autre cas**, et
c'est le plus intéressant des deux : celui où l'apprenant vient de le produire
correctement.

**Statut :** à étendre, pas à construire. Le mécanisme est en place dans
`_acknowledgement`, il ne couvre que le cas raté.

### C'est en variant qu'on gère le rythme
*Proposé par Meo. C'est la phrase qui compte : la variation n'est pas un remède
contre l'ennui, c'est l'instrument qui produit le rythme.*

Une leçon dont tous les tours ont la même forme n'a pas un rythme monotone —
elle n'a **pas de rythme**. C'est un métronome. Le rythme naît du contraste : un
tour long, puis trois courts ; une phrase qui raconte, puis une question sèche.

**Mesuré le 11 août** sur les 56 tours scriptés du cours :

```
 3 mots  █
 7 mots  ███████████████   ← le pic
 9 mots  ███████
12 mots  ███████
13 mots  ███████
36 mots  █                 ← le seul hook du roster
```

Médiane 9 mots, presque tout entre 7 et 13. Le seul tour qui sort du lot est
celui qui porte un fait. Le métronome, chiffré.

**Ce qui doit rester fixe, ce qui doit bouger.** C'est la distinction qui évite
de tout casser :

- **le signal reste fixe** — la forme de la question. « and again, what was ___ ? »
  doit être reconnaissable en trois occurrences, sinon l'apprenant redécode
  l'anglais au lieu d'écouter le vietnamien.
- **la texture bouge** — la longueur du tour, la présence ou non d'une phrase
  avant la question, un fait, une digression, trois rappels enchaînés vite puis
  un seul posé lentement.

Varier le cadre de la question serait donc une erreur ; varier tout le reste est
le sujet.

**Ce que ça veut dire concrètement**, et ce n'est pas une seule chose :

- un tour qui ne demande rien et raconte (« le café au Vietnam, c'est… »), puis
  on ré-enchaîne — ce serait une **étape** de plus dans `build_plan`
- des hooks beaucoup plus fréquents, pour que la longueur des introductions
  varie d'elle-même
- ~~des séries de rappels de longueur inégale, au lieu de trois systématiques~~
  **fait** le 11 août : `rapidfire_count` tire de 1 à 5 autour de la moyenne 3
  mesurée, et le nombre suit ce que le tour vient de faire — 1 après une
  construction qui a déjà fait réciter ses pièces, 4 après une règle où
  l'apprenant n'a rien dit. Le premier des trois leviers, et le seul qui ne
  demandait aucun contenu à écrire.

**La mesure qui décide :** le profil de longueur des tours du cours de
référence. Pas « est-ce qu'il digresse » mais « quelle est sa distribution ».
Si elle est plate comme la nôtre, il n'y a rien à faire. Si elle est étalée, on
sait de combien.

**Ce qui joue contre :** un tour sans question dépense de la synthèse sans faire
parler l'apprenant, et la règle 3 dit qu'il doit parler au moins autant que le
tuteur. La longueur des digressions compte autant que leur fréquence.

**Un levier est déjà en place — SPEC 17.** Le nombre de rappels qui closent un
item varie de 1 à 4, et pour l'argument exact de cette entrée : fixé à trois, un
apprenant attentif apprenait la cadence et répondait au rythme plutôt qu'à la
question. Ce tiers-là est fait et mesuré. Restent le tour qui raconte sans rien
demander, et des hooks plus fréquents.

**Statut :** à mesurer pour ce qui reste. C'est l'idée qui a le plus de chances de changer
la sensation du cours, et celle qu'il ne faut surtout pas régler à l'aveugle.

### Décomposer un nom connu, pour en enseigner deux d'un coup
*Proposé par Meo.*

→ Un **`strand`**, un fil qui n'existe pas encore : c'est cette entrée qui dit
pourquoi. Voir « Les traits : deux natures, pas une ».

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

**Vérifié en ligne le 11 août — et ça découvre une faille.** `Hà Nội` = 河內,
`hà` fleuve + `nội` dedans, la ville étant enserrée par le fleuve Rouge et la
Tô Lịch. Le fait est juste.

Mais `hà` et `nội` sont des morphèmes **liés** : le mot courant pour fleuve est
`sông`, pour dedans c'est `trong`. Donc Hà Nội est une belle anecdote et
**n'enseigne aucun mot utilisable**. Alors que `sân bay` = `sân` (cour) + `bay`
(voler), deux mots **libres**, employables seuls.

**La mesure de « 1 sur 5 » compte les deux cas ensemble, donc elle est
optimiste.** Figurer dans une liste de fréquence ne veut pas dire être un mot
libre *dans ce composé-là* : c'est exactement le cas `thông tin`, où `thông`
sort du dictionnaire en « river » alors qu'il porte ici 通, « faire passer ».

Deux usages distincts, à ne pas confondre :
- **morphèmes libres** (`sân bay`, `làm việc`, `bắt đầu`) → enseignent un
  deuxième mot, c'est l'idée d'origine
- **morphèmes liés** (`Hà Nội`, `thế giới`, `tổ chức`) → une anecdote qui aide
  la mémoire, mais pas de vocabulaire en plus

**Un troisième cas, trouvé le 13 août, que le test libre/lié laisse passer.**
`nhớ ra` = se souvenir d'un coup. `nhớ` (se souvenir) et `ra` (sortir) sont tous
deux des mots **libres** — le test passe — et la décomposition ment quand même :
ce `ra` ne veut pas dire « dehors », il marque le résultat. Pareil pour `nghĩ ra`
(trouver une idée) et `tìm ra` (trouver après avoir cherché).

Donc le test complet a deux conditions, pas une : les morceaux doivent être
libres, **et** le sens du tout doit se déduire des parties. `sân bay` passe les
deux. `Hà Nội` échoue la première. `nhớ ra` échoue la seconde.

**Limite honnête :** ça marche sur les composés sino-vietnamiens, pas sur tout.
`phở` ne se décompose pas. C'est un type de hook, applicable là où il s'applique
— pas une règle à forcer partout.

**Piste, pas encore creusée :** si les morceaux sont de vrais mots, ils
pourraient devenir des items à part entière. `bay` mériterait sa place après
`sân bay` — l'apprenant le rencontrerait deux fois, une fois caché dans
« aéroport », une fois pour lui-même.

**Statut :** câblé dans `fill_item_metadata.py`, pas encore vérifié sur des
propositions réelles.

---

## 2. Ce qui n'est encore qu'une idée

Rien dans le code ne les exécute. Chacune porte le tiroir qu'elle viserait et le
test qui reste à faire avant d'y toucher.

### La phrase est un véhicule, pas une destination
*Proposé par Meo, 15 août.*

**Ce qu'on suit, ce sont les mots et le réflexe de construire.** Une phrase doit
être juste, mais elle est jetable : elle a servi dès qu'elle a fait produire
quelque chose. On ne répète donc pas six fois `tôi ăn cơm` — on fait revenir `ăn`
et `cơm` six fois, dans six phrases différentes : une avec un autre pronom, une
au passé, une avec un adjectif en plus, une à la forme négative.

**Ce qui l'a déclenchée — mesuré le 15 août.** Sur les 149 mots enseignés,
**93 (62 %) ne figurent dans aucune phrase**. Ils ne peuvent revenir que par un
rappel sec. Et le cours de référence fait l'inverse : `to` est entendu **60 fois
en huit minutes** de japonais, parce qu'il voyage dans chaque phrase construite
(`METHOD.md`).

**Ce que ça annule.** La réponse évidente était d'écrire 93 phrases à la main.
Si la phrase est jetable, elle n'a besoin ni de nom, ni de niveau, ni de tirage —
donc il n'y a presque rien à écrire.

**Ce que ça débloque.** L'objection sérieuse à la génération était que rien ne
distingue `uống cà phê` de `uống cơm` — ni Wiktionary, qui n'atteste que les
expressions figées, ni `vn_freqs.tsv`, qui ne contient que des mots isolés. Mais
l'objection ne vaut que pour la **combinaison libre**. Une **transformation** de
phrase déjà validée reste juste : `tôi ăn cơm` correct ⇒ `anh ăn cơm`,
`tôi không ăn cơm`, `tôi đã ăn cơm` corrects.

**Et les opérateurs existent déjà : ce sont les traits.**

| trait | ce qu'il fait à une phrase |
| --- | --- |
| `không` | la nie |
| `đã` · `rồi` · `đang` · `sẽ` | la déplacent dans le temps |
| `có … không ?` | en fait une question |
| `ấy` | change la personne dont on parle |
| `rất` · `lắm` | intensifient |
| adjectif sans `là` | permet de qualifier le sujet |

Ce ne sont pas des règles à connaître, ce sont **des boutons pour fabriquer la
variation suivante**. Le classement en tiers prend alors un second sens : le
tier 1 est l'ensemble des boutons sans lesquels on ne peut rien varier.

**L'étape `vary` est déjà cette idée, en tout petit** — elle ne varie que la
personne, soit un bouton sur dix.

**Tiroir :** un geste qui revient → une étape dans `build_plan`. Pas un nouveau
`kind` : une phrase-souche reste une `construction`, et le carnet met en garde
contre la taxonomie.

**Ce qu'il faut avant d'y toucher :**

1. **Des phrases-souches validées.** Peu, mais justes. Huit combinaisons sont
   déjà écrites dans le contenu comme illustrations de règles et ne sont
   enseignées nulle part : `ăn cơm`, `uống cà phê`, `uống nước`, `cà phê ngon`,
   `cơm ngon`, `em mệt`, `tôi biết`, `cà phê của tôi`.
2. **Savoir quel trait s'applique à quelle souche.** Nier `tôi biết` marche ;
   mettre `cà phê ngon` au passé, non. C'est de la connaissance de vietnamien,
   donc de l'annotation, pas du code.
3. **Mesurer avant de câbler.** Combien de variations distinctes une souche
   supporte-t-elle réellement ? Si c'est deux, l'idée ne vaut pas sa complexité.

**Mesuré le 15 août — le verrou saute.** Croisement des 8 souches validées avec
les 27 traits `discrete`, en ne gardant que la compatibilité structurelle (`đã`
exige un verbe, `rất` un adjectif, `ấy` un mot de personne) :

```
tôi biết                              21 traits applicables
ăn cơm · uống cà phê · uống nước      19 chacune
em mệt                                 8
cà phê của tôi                         7
cà phê ngon · cơm ngon                 6 chacune
                                     ---
                        105 variations au premier niveau
```

**105 est un plafond, pas un résultat** : c'est de la compatibilité de forme, pas
du vietnamien. `hơn` s'applique à `cơm ngon` et donne `cơm ngon hơn`, à quoi il
manque un terme de comparaison — compté, et à jeter. Le vrai nombre sort de la
relecture, et **une phrase grammaticale que personne ne dit est pire qu'une
phrase en moins** : elle s'installe comme réflexe.

Mais le test posé plus haut était « si une souche ne donne que deux variations,
l'idée ne vaut pas sa complexité ». La moyenne est de **treize**. Même en jetant
les deux tiers, huit souches déjà écrites donnent une trentaine de phrases.

**Et ça dit où porter l'effort :** une souche **verbe + nom** vaut trois fois une
souche **nom + adjectif** (19 contre 6), parce que la plupart des traits agissent
sur le verbe — le temps, la négation, la question, l'obligation. Les souches à
écrire sont donc des phrases avec un verbe, pas des descriptions.

### Un tour, trois choses

```
tôi đã ăn cơm
 │   │   └── les mots   : tôi, ăn, cơm reviennent
 │   └────── le trait   : đã est réappliqué
 └────────── le réflexe : construire, pas réciter
```

Le trait ne revient plus par une étape séparée — il revient **dans le tour même**
qui fait revenir les mots. C'est plus économique que `0005`, où une application
de trait occupe un tour entier pour elle seule.

### Ce que ça rouvre, et qu'il faut trancher avant de câbler

`0005` a décidé **explicitement** de ne pas compter les mots employés dans une
phrase : *« l'application les exerce, mais le code n'enregistre rien pour eux »*.
C'était juste quand une application était un exercice de trait. **Ça devient faux
si la phrase est le véhicule des mots** — le niveau de `ăn` dirait qu'il n'a pas
été travaillé alors qu'il vient d'être produit dix fois.

**Décision de Meo, 15 août :** on compte l'exposition des mots dans la phrase, et
le niveau est redéfini une fois pour toutes — **« combien de fois l'apprenant a
produit ce mot »**, quelle qu'en soit la forme. C'est exactement ce que compte
`METHOD.md` quand il relève `to` soixante fois.

**Statut :** mesuré, et à câbler. Il reste à écrire les souches et à faire
relire les variations — le code ne peut pas décider qu'une phrase se dit.

### Dire ce qu'un mot va construire, au moment où on l'apprend
*Proposé par Meo, 13 août.*

L'idée du dessus prise dans l'autre sens. La décomposition paie **au composé** :
on arrive sur `sân bay` et on récolte `sân` et `bay`. Celle-ci paie **à l'atome** :
au moment où on enseigne `đi`, on dit qu'il servira à en fabriquer d'autres.

Le même fait, raconté à deux moments différents — et le second transforme un mot
ordinaire en investissement. L'apprenant ne range pas « aller », il range une
pièce.

**Tiroir :** geste qui revient → une formulation en code, dans `_INTRODUCE`.

**Ce qui la rend meilleure que sa jumelle : elle ne coûte aucune annotation.**
La décomposition arrière a besoin qu'un humain ou un modèle juge chaque composé
— c'est tout le travail des glosses, avec le risque d'invention. Celle-ci se
calcule : `pieces` existe déjà sur les items, il suffit de l'inverser. Au moment
d'introduire un mot, on regarde quels items pas encore enseignés le contiennent
dans leurs `pieces`. Zéro champ nouveau, zéro appel au modèle, et **aucune
invention possible** : le code ne peut nommer que des items qui existent.

**Le garde-fou.** C'est une promesse. Deux façons de la trahir :

- annoncer un composé que le séquencement n'atteindra jamais → ne compter que
  les items réellement enseignables, prérequis satisfaits ;
- nommer le composé, c'est l'enseigner en avance et donner la réponse d'un
  rappel futur — la famille de bugs de `_leaked_target`.

D'où la forme probable : **le nombre, pas les mots.** « Celui-là en construira
quatre autres plus tard. » Ça crée l'attente sans rien dépenser.

**Combien de mots sont concernés — mesuré le 13 août** sur notre roster, en
inversant `pieces` :

```
120  mots enseignés
 43  sont pièce d'au moins un autre item          plus d'un sur trois
```

```
tôi, ăn      pièce de 5 items
là, muốn, không, anh, chị    pièce de 4
```

Donc l'annonce aurait lieu sur plus d'un mot sur trois — assez pour que ce soit
un geste régulier, pas une curiosité. Et le chiffre ne peut que monter : il est
plafonné par le nombre de constructions écrites, aujourd'hui cinq.

**Pas encore mesuré** dans le cours de référence, en revanche. À compter :
est-ce qu'il annonce qu'un mot resservira, ou est-ce qu'il le laisse découvrir ?
L'intuition dit que oui et souvent — ce serait la marque de fabrique de la
méthode — mais l'intuition ne vaut rien ici, c'est la règle du carnet.

**Statut :** à essayer, et la moins chère des deux.

### Les mots qu'on reconnaît déjà — la couche française
*Proposé par Meo.*

Y a-t-il des mots vietnamiens qu'un anglophone reconnaît ? **Oui, mais pas par
l'anglais : par le français.** La colonisation a laissé une couche d'emprunts,
et une partie d'entre eux passe aussi en anglais.

Vérifié en ligne le 11 août ([Vietcetera], [Saigoneer], [Berlitz]) :

```
cà phê    ← café          reconnaissable en anglais aussi
xà lách   ← salade        salad
xiếc      ← cirque        circus
cà rem    ← crème         cream
pa tê     ← pâté          l'anglais l'emploie tel quel
ga tô     ← gâteau
ti vi     ← TV            emprunt direct à l'anglais
```

Et ceux qui ne marchent **que** pour un francophone :

```
xà phòng  ← savon      bơ  ← beurre      phô mát ← fromage
ga        ← gare       ốp la ← œuf au plat
```

**Deux d'entre eux sont déjà dans votre roster** : `cà phê` et `ga`.

**Tiroir :** un champ sur l'item → c'est le `hook`, troisième forme après le
fait et la décomposition.

**⚠ Ça contredit une règle du prompt**, et la contradiction est instructive :

> *« Vietnamese shares almost no vocabulary with English, so **never invite
> cognate guesses**. »*

Cette règle a raison sur le fond — un apprenant ne peut **pas deviner**, et un
modèle laissé libre inventerait des faux amis. Mais elle interdit aussi de
signaler un emprunt réel quand il y en a un.

La résolution est celle de tout le reste : **ne pas laisser le modèle
improviser, mettre l'emprunt vérifié dans le `hook`.** Interdire les devinettes
et fournir les faits sont deux choses différentes. Si on câble ça, la règle du
prompt doit être reformulée en même temps — sinon elle se battra contre les
hooks, comme le prompt s'est battu contre les tons.

**Et ça dépend de la langue de l'apprenant, pas de celle du cours.** La liste
est bien plus riche pour un francophone — et Meo l'est. Le cours se donne en
anglais, donc aujourd'hui on ne peut viser que l'intersection. Connaître la
langue maternelle de l'apprenant débloquerait la couche entière : encore une
chose que le profil rendrait possible.

**Statut :** à câbler avec les hooks, en reformulant la règle du prompt le même
jour.

[Vietcetera]: https://vietcetera.com/en/cocottes-curated-guide-to-french-loanwords-in-vietnamese
[Saigoneer]: https://saigoneer.com/saigon-culture/1160-words-loaned-by-the-french-borrowed-by-the-vietnamese
[Berlitz]: https://berlitzvietnamonline.com/blogs/news/french-words-in-everyday-vietnamese

### Dire de temps en temps ce qu'on sait déjà dire
*Observé pendant les séances du 11 août.*

Le cours ne fait **jamais** l'inventaire. Mot, question, mot, question — et à
aucun moment quelqu'un dit *« vous avez maintenant treize mots, et avec ça vous
savez déjà dire votre nom, demander celui des autres, et dire que quelque chose
n'est pas quelque chose »*.

C'est la signature la plus citée de la méthode de référence, et elle est
totalement absente ici.

**Ce n'est pas de la flatterie, c'est un fait.** Le code le calcule exactement,
sans rien inventer — vérifié le 11 août :

```
après  5 items :  3 mots, et vous savez dire « my name is ___ »
après 12 items :  8 mots, plus « what is your name? »
après 20 items : 13 mots, 3 phrases — et vous avez déjà tout
                 pour « want ___ », qui n'a pas encore été enseignée
```

Cette dernière ligne est la plus intéressante : le code sait quelles phrases
sont **déjà déblocables** parce que toutes leurs pièces sont apprises. Dire
« vous avez déjà tout ce qu'il faut pour la suivante » est une promesse tenue
d'avance.

**Tiroir :** une **étape** dans `build_plan`, insérée tous les N items — le
même véhicule que la digression du carnet, et le même argument de rythme : un
tour long qui raconte, entre des rappels courts.

**Ce qui joue pour :** c'est le seul retour d'ensemble que l'apprenant puisse
recevoir. Aujourd'hui il n'a que « That's it » au tour par tour, qui ne dit rien
de la trajectoire. Et un cours par la voix n'a aucun tableau de bord — pas
d'écran, pas de barre de progression : s'il ne le dit pas, personne ne le sait.

**Ce qui joue contre :** la même chose que pour la digression — un tour sans
question dépense de la synthèse sans faire parler l'apprenant. Et à 2000 mots
l'inventaire devient absurde : il faudra compter plutôt qu'énumérer, ou ne citer
que ce qui vient d'être débloqué.

**La mesure qui décide :** à quelle fréquence le cours de référence fait-il cet
inventaire ? Toutes les cinq minutes, à chaque fin de section, une seule fois ?
Et cite-t-il les phrases ou seulement le nombre ?

**Statut :** à mesurer. C'est la moins chère des trois idées de rythme — le
calcul existe, il n'y a rien à écrire comme contenu.

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

### Le second sens d'un homophone, à la seconde rencontre
*Proposé par Meo, 13 août.*

`nam` 男 « masculin » et `nam` 南 « sud » : deux mots d'origine différente
tombés sur la même syllabe. Pas « orange » le fruit et la couleur — plutôt
« ver / vert / verre ». Le vietnamien en est plein, parce que l'inventaire de
syllabes est petit et que les emprunts chinois se sont empilés dessus.

À ne pas confondre avec les jumeaux de ton : `ba` et `bà` ne sonnent pas
pareil, un natif ne les confond jamais, c'est un obstacle d'oreille étrangère.
Un homophone est ambigu **pour tout le monde**, et se résout par le contexte.

**Quand le dire : à la seconde rencontre, jamais à l'introduction.** Même règle
que pour les jumeaux de ton, et pour une raison qui n'est pas une préférence —
**le gloss EST la question du rappel**, lu à voix haute par `speakable(gloss)`.
Deux sens dans un gloss donnent « le mot pour sud… ou masculin ? », une question
sans réponse unique. Le second sens est donc un aparté, pas une définition.

À l'introduction c'est une charge doublée sur un mot qu'on ne tient pas encore.
Au retour, c'est un cadeau : un son déjà acquis, un deuxième mot rangé.

**La contrainte que ça révèle, et elle est structurelle.** Tout le code indexe
les items **par leur nom** : les prérequis, le SRS, les pièces des
constructions, la déduplication de `load_course`. Donc un homophone ne peut
jamais être deux items — ils s'écraseraient ou seraient signalés en doublon.

C'est forcément **un item plus une note**. Et donc **le SRS ne suivra jamais que
l'un des deux sens** : le second sera dit, entendu, et jamais redemandé. Écrit
ici pour qu'on ne se demande pas dans un mois pourquoi il ne revient pas.

**Tiroir :** un champ sur l'item, dit par une formulation en code au retour.

**Le piège des données.** Le second sens ne s'automatise pas : Wiktionary donne
`là` = « fine silk » et `tôi` = « esclave », ses premiers sens sont les
archaïques. Même passe d'annotation que les glosses, même consigne « ne devine
jamais ».

**Pas chiffrable avec ce qu'on a.** Chaque mot ne figure qu'une fois dans la
liste, donc `nam` masculin et `nam` sud sont un seul item pour le code. Les
paires de casse trouvées le 13 août (`Nam`/`nam`, `Bắc`/`bắc`, `Tết`/`tết`) ne
sont que la partie où l'orthographe trahit la différence. Compter les vrais
demanderait un dictionnaire de sens.

**Statut :** à écrire dans la consigne d'annotation, pas à câbler.

---

### Le troisième moment : quand la dernière pièce tombe
*Proposé par Meo, 13 août.*

Les deux entrées ci-dessus placent la décomposition à deux instants. Meo en
désigne un troisième, et c'est le meilleur : **le moment où le second morceau
est enseigné**, avant même que le composé arrive.

```
au composé   (« Décomposer un nom connu »)   la 1re pièce peut dater de 3 semaines
à l'atome    (« Dire ce qu'un mot va… »)     la 2e pièce n'existe pas encore
à la 2e pièce  ← celui-ci                    les DEUX moitiés sont fraîches
```

C'est le seul des trois où l'apprenant a les deux morceaux en tête en même
temps. Et c'est le même calcul que le deuxième, avec un filtre plus strict —
donc un seul mécanisme à construire, pas deux.

**Mesuré le 13 août, et le chiffre dit de ne pas le câbler tout de suite :**

```
il se déclencherait   2 fois   sur tout le cours actuel
   en enseignant xin  ->  Xin chào devient composable
   en enseignant sao  ->  không sao devient composable
```

Deux. Parce que le cours n'a que 27 mots multi-syllabes enseignés, et que leurs
syllabes ne sont presque jamais enseignées séparément. Les 428 composés
décomposables mesurés le matin sont tous dans le **stock muet**.

**Le vrai blocage, trouvé en cherchant à le construire :** aucun atome ne porte
de décomposition. `pieces` existe et vaut zéro sur zéro atome — le champ ne sert
qu'aux constructions et aux règles. Donc **les trois moments sont bloqués par la
même donnée manquante**, et elle appartient à la passe d'annotation, pas au code.

Le découpage par syllabes du nom est calculable sans annotation, mais il ment
une fois sur deux (`cho nên`, `bà con`, `con cái` — mesuré). Il ne peut servir
qu'à proposer des candidats à vérifier, jamais à parler.

**Statut :** à ne PAS câbler maintenant. Le mécanisme firerait deux fois. À
reprendre le jour où les décompositions sont écrites — et ce jour-là les trois
moments arrivent ensemble, puisqu'ils attendent la même chose.

### Demander à l'apprenant d'inventer sa propre phrase
*Proposé par Meo, 14 août.*

À un moment, arrêter de demander « comment dirais-tu X ? » et demander **une
phrase à lui**, avec ce qu'il a.

**C'est le seul tour où l'apprenant choisirait le contenu.** Aujourd'hui, sans
exception, le tuteur décide quoi produire et l'apprenant restitue. Or le but du
cours est de parler à des gens qui, eux, ne fourniront jamais la phrase. La
différence entre réciter et parler est exactement là.

**Tiroir :** un geste qui revient → une étape dans `build_plan`, du même genre
que `apply`. Probablement pas à chaque item : à un palier, quand une
construction vient d'être consolidée — « maintenant, dites-moi quelque chose à
vous avec ces cinq mots ».

**Sœur de « dire ce qu'on sait déjà dire ».** L'inventaire annonce ce qui est
possible ; celle-ci le fait prouver. Les deux au même palier se tiendraient
bien : voilà ce que vous savez dire, maintenant dites-en une.

**Ce qui joue contre, et c'est sérieux.** Le code ne peut pas juger une phrase
libre : `answered_target` compare à une cible connue, et ici il n'y a pas de
cible. **Donc le modèle doit juger** — précisément ce que cette journée entière
a consisté à lui retirer. Chaque fois qu'on lui a laissé la bride, il a validé
`tôi cơm ngon`, corrigé une réponse juste, inventé une erreur jamais commise.

Une phrase inventée par l'apprenant et validée à tort est **pire** qu'un rappel
raté : elle installe une faute avec un tampon d'approbation.

Deuxième obstacle : la reconnaissance. Une phrase libre est longue, et les
longues transcriptions sont les pires — mesuré toute la soirée.

**La sortie possible :** ne pas juger. Le tuteur écoute, Minh redit une version
correcte, et on avance — sans verdict. C'est ce que le cours fait déjà pour la
prononciation, où il ne peut pas non plus corriger : donner un modèle, jamais
un jugement. La même honnêteté marcherait ici.

**À mesurer :** le cours de référence demande-t-il jamais d'inventer ? Mon
intuition dit rarement et tard, parce que sa force est justement de ne jamais
laisser l'apprenant sans filet. Si c'est zéro fois en vingt-cinq minutes, c'est
une préférence — et alors on l'essaie en le sachant.

**Statut :** à mesurer d'abord. Et à ne pas câbler tant que le tour de règle
n'est pas scripté : ce serait ajouter un endroit où le modèle juge, le jour où
on cherche à en retirer un.

---

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

Et sur nos propres tours, mesuré le 11 août :

- **56** tours scriptés, longueur médiane **9 mots**, presque tous entre 7 et 13
- un seul dépasse 17 mots : celui qui porte un `hook`

---

---

## Ce que les trois idées de Meo ont en commun

*Le tri a séparé les trois entrées : la composition et le jumeau de ton
tournent déjà (partie 1), l'homophone est encore une idée (partie 2). Ce qui
suit est ce qu'elles partagent, et qui ne dépend pas de leur état.*

Elles sont arrivées séparément le 13 août et ce sont la même :

| | on paie… | on encaisse… |
| --- | --- | --- |
| **composition** | à l'atome (`đi`) | au composé (`đi học`) |
| **jumeau de ton** | au premier mot (`ba`) | au second (`bà`) |
| **homophone** | au premier sens (`nam` sud) | au retour (`nam` masculin) |

**La deuxième rencontre est celle qui rapporte.** La première pose une brique
qui ne paie pas encore ; c'est en revenant dessus qu'on récolte, et sans rien
avoir à mémoriser de neuf.

Ce qui donne un test commun, plus utile que trois règles séparées : *pour cette
idée, qu'est-ce qui est posé la première fois, et qu'est-ce qui est encaissé la
seconde ?* Si la réponse est « tout, tout de suite », ce n'est pas de cette
famille — et il faut se demander si ça double la charge au lieu de la répartir.

# Ce que le cours enseigne — brouillon d'objectifs

*Proposé par Meo, 13 août. À corriger : barrer, déplacer, ajouter.*

**Autre sujet que le reste du fichier.** Le carnet ci-dessus dit comment le
tuteur PARLE ; ceci dit ce que le cours ENSEIGNE. Rangé ici parce que ce n'est
qu'une idée — rien dans le code ne le lit, aucun champ n'existe pour ça. Si ça
prend, ça sort dans son propre fichier.

## À quoi ça sert

À une seule question, posée à chaque item : **« quel objectif en a besoin ? »**

- aucun objectif → c'est un mot niche, il reste au stock
- un objectif l'attend → il entre, et on sait à quel moment
- un objectif n'a aucun item → c'est le vrai travail restant, pas mon inventaire

Et surtout : **18 lignes se relisent, 200 items non.** C'est ce qui permet de
contrôler les choix de contenu sans lire le roster.

## Les 18

Ordre = ordre d'enseignement. `✓` acquis, `✗` manquant.

| # | savoir faire | ce qu'il faut |
| --- | --- | --- |
| 1 | **dire qui je suis** | ✓ tôi, tên, là, gì |
| 2 | **choisir comment m'adresser à quelqu'un** | ✓ anh, chị, em, bạn, cô, chú, ông, bà, cháu, mình + les règles de xưng hô |
| 3 | **saluer, remercier, m'excuser** | ✓ chào, cảm ơn, xin lỗi, không sao, dạ, vâng, ạ |
| 4 | **dire ce que je veux et ne veux pas** | ✓ muốn, cần, thích, không |
| 5 | **poser une question fermée et y répondre** | ✓ có…không?, chưa? + la réponse en écho |
| 6 | **commander à manger et à boire** | ✓ ăn, uống, cơm, cà phê, nước, ngon, này &nbsp;·&nbsp; ✗ de quoi nommer un plat |
| 7 | **demander un prix, comprendre la réponse** | ✓ bao nhiêu, tiền, mua, bán &nbsp;·&nbsp; ✗ **les nombres au-delà de 10** (mươi, lăm, mốt, tư, trăm, nghìn) |
| 8 | **dire où je suis et où je vais** | ✓ ở, đi, về, ra, vào, lên, xuống, đến, trong, trên, dưới &nbsp;·&nbsp; ✗ la règle des verbes en série, les lieux (nhà, đường, khách sạn) |
| 9 | **parler de quelqu'un d'autre** | ✓ ấy + sa règle, người |
| 10 | **situer dans le temps** | ✓ hôm nay, hôm qua, ngày mai, đã, đang, sẽ, rồi, chưa &nbsp;·&nbsp; ✗ bây giờ, giờ |
| 11 | **dire ce que je peux, dois, devrais faire** | ✓ phải, có thể, nên, được, đừng |
| 12 | **décrire et comparer** | ✓ ngon, đẹp, mệt, đói, buồn, rất, lắm, hơn, nhất + adjectif sans « là » |
| 13 | **compter des choses** | ✓ cái, con, người, quả, chiếc + la règle des classificateurs |
| 14 | **demander de l'aide, me faire comprendre** | ✓ giúp, hiểu, biết, nói, chờ, ơi &nbsp;·&nbsp; ✗ « répétez », « lentement », « je ne comprends pas » |
| 15 | **raconter ma journée** | ✓ ngủ, làm, học, chơi, đọc, viết, nghe, gặp, tìm, lấy |
| 16 | **donner une raison, dire ce que je pense** | ✓ vì, thấy, nhớ, quên, nghĩ &nbsp;·&nbsp; ✗ de quoi enchaîner deux idées |
| 17 | **inviter, proposer, encourager** | ✗ **les particules finales** (nhé, đi, à, hả) + l'impératif positif |
| 18 | **tenir la conversation** | ✓ còn, nữa, và, nhưng &nbsp;·&nbsp; ✗ relancer, changer de sujet |

## Ce que la liste dit tout de suite

**Trois objectifs sont bloqués par du contenu manquant, pas par de l'ordre :**
le 7 (les nombres), le 8 (les verbes en série), le 17 (les particules, où rien
n'existe du tout). C'est ça la liste de travail — et elle est courte.

**Quinze sur dix-huit sont déjà servis** par les 124 mots enseignés. Le cours
est plus complet qu'il n'en a l'air ; ce qui manquait, c'était de pouvoir le
voir.

## Ce dont il faut se méfier

Que ça devienne une taxonomie. Un objectif se déplace en une ligne — le coût
n'est jamais dans le découpage, il est dans le temps passé à en débattre.

Et la règle du carnet vaut ici aussi : **un objectif qu'on ne peut pas
illustrer par une chose qu'on dirait vraiment à quelqu'un au Vietnam est une
préférence, pas un objectif.**

---

# Les traits : deux natures, pas une

*Établi le 15 août, session « Tours mécaniques automatisés ». **Le classement en
tiers n'a jamais été validé par Meo** — c'était une proposition, elle attend
d'être barrée, déplacée, corrigée.*

**Ce n'est pas une taxonomie.** A et B ne sont pas deux étiquettes sur la même
chose : ce sont **deux mécanismes**, qui demandent deux codes différents. C'est
tout l'intérêt de la distinction, et la seule raison de la garder.

**Où vit quoi.** La classification elle-même — A ou B, quel tier — n'est **pas**
dans `SPEC.md`, et c'est normal : elle n'est pas encore dans le code. Ce qui y
est, ce sont les **fils** eux-mêmes, chacun avec sa règle. La colonne du milieu
ci-dessous donne le numéro. Le jour où `0001` écrit la classification dans les
items, elle deviendra active et recevra sa propre règle dans `SPEC.md`.

**Comment lire cette page avec le reste du carnet.** Ici on tranche : quelle
nature, quel tier, quel mécanisme existe ou manque. Le **pourquoi pédagogique et
les mesures** restent dans les entrées du carnet plus haut, et chaque ligne dit
laquelle. Aucun fait n'est écrit deux fois — et le détail n'est pas décoratif :
c'est lui qui dit **comment** coder la chose. Une catégorie sans son entrée de
carnet donne le classement et perd la méthode.

Le code traitait les 35 traits à l'identique : un `kind = "feature"`,
une position dans la file, enseigné, terminé. Le futur et les tons sont modélisés
pareil. C'est ça, l'erreur.

## Les fils continus — `strand` (7)

**Ce ne sont pas des items, ce sont des dimensions.** Le ton s'attache à *chaque
mot*. Le système de pronoms s'attache à *chaque phrase contenant une personne*.
Ça ne peut pas avoir de position, parce que ça n'a pas de fin.

| l'item aujourd'hui | le fil existe-t-il déjà ? | le détail, plus haut dans ce fichier |
| --- | --- | --- |
| les tons : écouter et copier | **oui** — `SPEC 28c`, la paire dite par Minh | « Les tons : donner un modèle, jamais un jugement » |
| le mot pour « je » change | **oui** — `SPEC 10b` (le profil) + `12d` | « Demander qui est l'apprenant, pour lui enseigner SES pronoms » |
| comment choisir son terme | **oui** — `SPEC 10b` + `13d` | idem |
| le terme change selon la paire | **oui** — `SPEC 12d` + `13d` | idem |
| la politesse est dans le mot d'adresse | **oui** — `SPEC 13d` | idem |
| coller deux mots connus | **NON** — `pieces` vaut 0 sur 2042 atomes, `hook` 1 | « Décomposer un nom connu » + « Le troisième moment » |
| compter de 11 à 99 | **NON** — aucun mécanisme nulle part | — rien d'écrit |

**Les quatre du milieu sont un seul fil découpé en quatre items**, parce que
l'item était le seul moule disponible. Pour six des sept, la version « fil »
existe déjà et enseigne mieux que la version item : ces items-là sont des
vestiges, à supprimer et non à réordonner.

**Deux des sept n'ont pas de fil**, et c'est ce qui décide de l'ordre des
travaux. Les supprimer retirerait de l'enseignement sans rien mettre à la place ;
ils restent des items tant que leur fil n'existe pas.

- **les nombres** — aucun mécanisme, nulle part.
- **coller deux mots connus** — la session du 15 août a répondu « oui, le
  `hook` », et c'est faux : mesuré, `pieces` vaut **0 sur 2042 atomes** et un
  seul atome porte un `hook`. Le carnet l'avait déjà établi le 13 août — *« les
  trois moments sont bloqués par la même donnée manquante, et elle appartient à
  la passe d'annotation, pas au code »*. Le fil n'est pas construit, il est
  **bloqué par du contenu à écrire**.

## Les faits ponctuels — `discrete` (28)

Ils restent des items avec une position. Ce qui leur manque, c'est **la seconde
moitié** : on ne peut pas *redemander* un trait, mais on peut le
*ré-appliquer*. Le véhicule existe déjà — l'étape `apply` — mais elle ne se
déclenche qu'à l'introduction.

**La mesure qui a produit cette page :**

```
33 traits enseignés sur tout le cours
niveau après le cours entier : min 0, max 0
jamais redemandés            : 33 / 33
```

Contre un niveau moyen de **4,5** pour les mots. Les traits sont explicitement
exclus du tirage des rappels — « nobody says a rule back », ce qui est vrai, et a
été pris pour « donc il n'y a rien à faire ».

**Toujours vrai au 15 août :** `tutor.py` → `exclude |= {i.name for i in
seen_items if i.kind == "rule"}`.

## Les tiers — les traits `discrete` classés par utilité

**Validé par Meo le 15 août.** La liste qui fait foi est le champ `tier` des
items ; ce qui suit est le *pourquoi* de chaque rang, qui ne vit nulle part
ailleurs.

**Tier 1 — on ne peut pas parler sans (8)**

| la règle | ce qu'elle dit |
| --- | --- |
| **les verbes ne changent jamais** | une seule forme, pour tout le monde. Une phrase et c'est compris — et elle pose aussitôt la question du temps |
| **`đã`** | le passé, juste avant le verbe. La réponse à la question que la précédente vient de poser, enseignée dans la foulée |
| **`không` + verbe/adjectif** | un mot devant, et c'est nié. Même mot pour les deux |
| **`có … không ?`** | on encadre la phrase pour questionner. Pas d'inversion, pas d'auxiliaire |
| **répondre en répétant le verbe** | on ne dit pas oui, on renvoie le verbe |
| **`ơi`** | héler — le premier mot de toute interaction avec un inconnu |
| **pas de `là` devant un adjectif** | « Em mệt », vingt fois par jour |
| **`ấy`** | sans lui on ne parle qu'**à** quelqu'un, jamais **de** quelqu'un |

**Tier 2 — très fréquent (10) :** `rồi` · `chưa` · `đang` · `sẽ` · `phải` ·
`ở`+`trong` · `của` · adjectif après le nom · `ạ` · classificateurs

**Tier 3 — confort et finition (9) :** ni genre ni article · pas de pluriel ·
mot interrogatif en place · omettre le sujet · `cũng` · `rất` avant / `lắm`
après · `hơn` · `được` · `năm` → `lăm`

**Retirée du cours le 15 août :** l'ordre sujet–verbe–objet. Elle était en tête
du tier 1 et sa fiche la présentait comme le filet du débutant — « dans le doute,
range comme en anglais et c'est souvent juste ». Décision de Meo : un francophone
le fait déjà sans y penser, donc la règle occupe un créneau pour enseigner un
réflexe acquis.

### Ce que le classement dit tout de suite

**Les tiers 1 et 2 sont presque tous en fin de cours ; le tier 3 presque tout au
début.** `ơi` en 106, `có…không ?` en 121 — des choses de la première minute
d'une vraie conversation, servies en dernier. L'ordre actuel suit les fichiers,
et la grammaire générale a été écrite avant le vocabulaire utile.

### Les trois incertitudes, telles quelles

- **les classificateurs** — la règle est un fait (nombre + classificateur + nom),
  mais **quel** classificateur pour quel nom est un fil : chaque nom nouveau
  apporte le sien. A pour la règle, avec un fil B latent qu'on ne modélise pas.
- **répondre en écho** — classé A parce que le fait se dit une fois. Mais c'est
  un réflexe qui vaut pour chaque question fermée, à jamais. Ce qui distingue un
  fil, c'est qu'il **s'approfondit** ; l'écho ne s'approfondit pas. Le plus
  discutable des vingt-six.
- **coller deux mots connus** — classé B, et c'est peut-être faux : c'est une
  stratégie de compréhension qui accompagne chaque mot composé rencontré, pas un
  fait qu'on range.

## Où vit la classification

**Dans les items, plus ici.** Chaque trait porte `nature` (`discrete` ou
`strand`) et, s'il est `discrete`, son `tier`. C'est la source ; ce fichier ne
la recopie pas.

Une table de rattachement a vécu ici une journée et s'est démentie en une
journée : écrite avec les valeurs `A` et `B`, elle est devenue fausse dès que
les items ont pris `discrete` et `strand`. Une donnée recopiée dérive — c'est
la même leçon que la ligne **Où** de `SPEC.md`, un cran plus bas.

Pour la lire, telle qu'elle est vraiment :

```bash
python -c "import glob,tomllib,sys; sys.stdout.reconfigure(encoding='utf-8'); [print(f\"{i['nature']:9s} {i.get('tier','-')}  {i['name']}\") for f in sorted(glob.glob('content/vietnamese/*.toml')) for k,v in tomllib.load(open(f,'rb')).items() for i in (v if isinstance(v,list) else [v]) if isinstance(i,dict) and i.get('kind')=='feature']"
```

Répartition au 15 août : **28 `discrete`** (7 + 11 + 10 sur les trois tiers) et
**7 `strand`**.

### Les deux rattachés après coup

`đang` et `sẽ` n'étaient dans aucune catégorie. Créés le **14 août** par « Split
the three tense markers into three rules, one each », donc **avant** la
classification, qui les a simplement oubliés.

**Rangés en `discrete`, tier 2, par Meo**, à côté de `đã`, `rồi` et `chưa` : même place
dans la phrase, même fréquence, même nature de fait ponctuel. Le tier 2 compte
donc **11** traits, pas 9, et les `discrete` **28**.

## Ce qui en découle, et qui n'est pas fait

1. **Retirer les 6 traits doublons** — petit, surtout du contenu.
2. **Faire revenir les applications** — l'étape `apply` tirée plus tard, pondérée
   par le même SRS que les mots. C'est là qu'est la valeur : le 33/33.
3. **Réordonner le cours selon les tiers** — contenu seul, zéro code, et bloqué
   tant que le classement n'est pas validé.

**Rien de tout ça n'est implémenté au 15 août.** Les sept items `strand`
existent toujours, l'exclusion du SRS tient, l'ordre du cours n'a pas bougé.
