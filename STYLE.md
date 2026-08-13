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

**Limite honnête :** ça marche sur les composés sino-vietnamiens, pas sur tout.
`phở` ne se décompose pas. C'est un type de hook, applicable là où il s'applique
— pas une règle à forcer partout.

**Piste, pas encore creusée :** si les morceaux sont de vrais mots, ils
pourraient devenir des items à part entière. `bay` mériterait sa place après
`sân bay` — l'apprenant le rencontrerait deux fois, une fois caché dans
« aéroport », une fois pour lui-même.

**Statut :** câblé dans `fill_item_metadata.py`, pas encore vérifié sur des
propositions réelles.

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

**Statut :** à mesurer d'abord. C'est l'idée qui a le plus de chances de changer
la sensation du cours, et celle qu'il ne faut surtout pas régler à l'aveugle.

### Demander qui est l'apprenant, pour lui enseigner SES pronoms
*Proposé par Meo.*

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

**Statut :** à faire. C'est probablement la personnalisation la plus rentable de
toute la langue — le système d'adresse est ce qui distingue quelqu'un qui parle
vietnamien de quelqu'un qui récite du vietnamien.

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

## Les notes de Meo

Attendues, pas encore intégrées. Quand elles arrivent : note par note, quel
tiroir — et lesquelles ne survivent pas au test.
