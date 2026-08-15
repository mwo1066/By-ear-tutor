# Ce que fait le tuteur

Chaque comportement en français, avec l'endroit où il est appliqué et ce qu'il
faut modifier pour le changer. Écrit à partir du code, pas de mémoire.

**Le vocabulaire de ce fichier est défini dans [`LEXIQUE.md`](LEXIQUE.md)** —
trait, atome, pièce, tour scripté, glose. À lire d'abord si tu arrives sur le
projet.

**Lis d'abord la ligne « Où ».** C'est la distinction qui compte le plus, et
celle qui nous a coûté le plus cher :

- **code** — une garantie. Le modèle ne peut pas la violer.
- **prompt** — une consigne. Il la suit la plupart du temps, et l'oublie le
  reste du temps.

Mettre une règle dans le prompt alors qu'elle pouvait être du code, c'est ce
qui a produit un tuteur récitant dix étapes d'un souffle et redemandant quatre
fois le même mot. Laisser une règle dans le prompt après l'avoir déplacée dans
le code, c'est ce qui a produit un marqueur que plus rien n'émettait.

---

## Les sections

| | ce qu'elle répond |
| --- | --- |
| [Les deux voix](#les-deux-voix) | qui parle, et dans quelle langue |
| [La forme d'un tour](#la-forme-dun-tour) | ce qu'un tour a le droit de faire, et qui l'écrit |
| [L'ordre du cours](#lordre-du-cours) | qu'est-ce qui vient après quoi |
| [Ce que le cours sait](#ce-que-le-cours-sait) | les données qu'il tient — sur les items, sur l'apprenant |
| [Enseigner un mot](#enseigner-un-mot) | un `atom` |
| [Enseigner une construction](#enseigner-une-construction) | une `construction` |
| [Enseigner un trait](#enseigner-un-trait) | un `feature` |
| [Comment les mots reviennent](#comment-les-mots-reviennent) | le niveau, l'espacement, les rappels |
| [Les réponses](#les-réponses) | comment une réponse est jugée, et ce qu'on en dit |
| [Entendre l'apprenant](#entendre-lapprenant) | le micro, le silence, la transcription |
| [L'ouverture](#louverture) | le tout premier tour |
| [La prononciation](#la-prononciation) | les tons, et ce qu'on se refuse à juger |
| [Les outils](#les-outils) | les trois appels que le modèle peut passer |
| [L'infrastructure](#linfrastructure) | le modèle, le budget, la sauvegarde |

Les trois sections « Enseigner… » suivent les trois sortes d'item du
[`LEXIQUE.md`](LEXIQUE.md), dans cet ordre. Les numéros de règle sont des
identifiants stables : ils ne se renumérotent pas quand une section bouge.

---

## Les deux voix

### 1. Deux locuteurs, aiguillés par la langue
Le tuteur parle la langue de l'apprenant, Minh uniquement le vietnamien.
 La
voix entendue est décidée par la langue dans laquelle chaque phrase est écrite
— le modèle ne pose aucune étiquette.
**Où :** code — `voice.split_by_voice` découpe **mot par mot**, jamais par
morceau entre deux espaces
**Pourquoi mot par mot :** cette ligne du SPEC était déjà juste, le code ne
l'était pas. Il découpait sur les espaces, puis classait un morceau entier
d'après sa première suite de lettres. Le modèle a écrit « That's correct—là. »
sans espace autour du tiret : un seul morceau, classé sur « correct », donc la
voix anglaise a prononcé « là ». La ponctuation n'est plus un séparateur qu'il
faut prévoir — elle suit simplement le mot qui la précède, ce qui vaut pour le
tiret, la barre oblique, les parenthèses et celles qu'on n'a pas vues.
**Changer :** `voice.py` → `TUTOR_VOICE`, `TEACHER_VOICE`, `_WORD_SPLIT_RE`

### 2. Les didascalies et le markdown sont supprimés
« Minh: » écrit comme une étiquette, ou `**gras**`, n'atteint jamais les
haut-parleurs. Et **une ligne qui ne contient rien d'autre qu'un nom de
locuteur n'est pas prononcée du tout**, quelle que soit la ponctuation autour.
**Où :** les deux — le prompt l'interdit, `voice._strip_markdown` et
`voice.is_stage_direction` le retirent quand même
**Pourquoi les deux :** le code empêche que ce soit *entendu*, seul le prompt
empêche le modèle de *penser* en listes à puces, ce qui aplatit la pédagogie
**Pourquoi « rien d'autre que le nom » :** l'ancienne règle exigeait un
deux-points. Le modèle a écrit « Minh: tôi. » une séance, « Minh. » la
suivante — la voix anglaise a annoncé « Minh » avant chaque réplique du prof,
deux fois. Ajouter le point corrigeait cette séance et pas la prochaine
(« Minh — », « (Minh) »). La liste des ponctuations est ouverte ; la liste des
**noms** est fermée, il y a deux voix.
**Changer :** `voice.py` → `_SPEAKER_NAMES`, `_SPEAKER_LABEL`, `_MARKDOWN_CHARS`

### 3. Un mot vietnamien dans une phrase du tuteur se place à la fin
Chaque changement de voix coûte un aller-retour de synthèse : un seul par
phrase, et à la fin.
**Où :** prompt
**Changer :** `persona.toml` → THE TWO VOICES

---

## La forme d'un tour

### 4. Une consigne par tour
Avant chaque tour, le modèle reçoit exactement une chose à faire. Il ne voit
jamais la suite du plan.
**Où :** code — `build_plan` construit la liste, `_lesson_note` n'en révèle
qu'une étape
**Pourquoi :** le modèle n'a aucune mémoire entre les tours. À qui on demande
de retenir où il en est, il dérive à chaque fois.
**Changer :** `tutor.py` → `build_plan`

### 4b. Les tours mécaniques sont écrits par le code, sans appel au modèle
Une étape est écrite ici dès que le code en tient les **deux moitiés** : le sens
à partir duquel demander (`ask`, tiré du seul `gloss`) et le mot qu'il ne faut
surtout pas dire (`target`). Elle est composée et envoyée directement à la
synthèse. S'il en manque une, le modèle reprend le tour — c'est une garde, pas
une liste d'exceptions.

Six sortes d'étapes sur les neuf remplissent la condition : `recall_piece`,
`rapidfire`, `settle`, `introduce`, `scaffold`, `apply`. Les deux dernières
seulement quand elles ont de quoi — un échafaudage sans ordre littéral, une
application sans phrase à demander, et le tour repart au modèle.

Restent au modèle, toujours : `answer` (réagir à la phrase qui vient d'être
produite), `rule` (nommer le motif) et `vary` (reposer la même phrase à
quelqu'un d'autre). Ce qu'il faut inventer.
**Où :** code — `scripted_turn` compose, `_speak_scripted_turn` prononce
**Pourquoi :** le modèle avait un tour de retard. Séance réelle : consigne
d'introduire « tên », il redemande « tôi » ; il introduit « tên » au tour
suivant, celui où dire le mot est interdit — la réponse donnée avant la
question, et un mot vietnamien qui surgit au hasard au milieu d'un exercice.
Une phrase composée ici ne peut ni sauter son étape, ni donner sa réponse, ni
prendre du retard. Elle divise aussi par deux le nombre de requêtes par leçon.
**Pourquoi la liste a grandi :** `introduce` et `scaffold` sont arrivés après
coup, chacun pour avoir dit le vietnamien sur le tour qui l'interdit.
L'échafaudage a demandé « can you say the full sentence tôi tên là… » —
c'est-à-dire la réponse — alors que son instruction disait « ne dis aucun
vietnamien » depuis le début. Une consigne que le modèle enfreint sur l'étape même qu'elle
protège est la définition d'une règle à déplacer dans le code.
**Garantie :** la question est bâtie à partir du seul `gloss`, jamais du nom
vietnamien — un rappel scripté ne peut donc pas contenir sa propre réponse.
`smoke_test.py` le vérifie à chaque exécution.
**Coût assumé :** on perd la réaction à ce que l'apprenant vient de dire. Ce
qu'il en reste est le verdict du code (18c), placé en tête de la phrase.
**Changer :** `tutor.py` → `SCRIPTED_KINDS`, `_REPEAT_ASK`, `_ACK_CORRECT`

### 4b-bis. Dire « j'ai oublié » donne toujours droit à la réponse
« I forgot », « no idea », « dunno » — le tour repart au modèle, qui donne le
mot, le fait redire par Minh une fois, et dit qu'il reviendra plus tard.
**Où :** code — `learner_gave_up`
**Pourquoi :** sur une étape de rappel, la reprise donnait déjà le mot. Mais sur
une étape écrite par le MODÈLE (règle, échafaudage, variation), le code ne sait
pas ce qui a été demandé, donc il ne peut ni juger ni redonner. Séance réelle :
« I forgot » fait deux mots, sous le seuil de 4c, donc la leçon a enchaîné comme
si rien n'avait été dit.
**Assumé :** c'est une liste, et ce projet se méfie des listes. Elle est gardée
parce qu'elle est fermée par autre chose que le code — il n'y a qu'un nombre
fini de façons de dire qu'on ne sait pas, et elle ne grandit pas quand un modèle
invente une tournure. Si elle se met à grandir, c'est le signal qu'il faut
trouver la propriété à la place.
**Changer :** `tutor.py` → `_GAVE_UP`

### 4c. Un apprenant qui parle vraiment rend la main au modèle
Une question, ou plus de deux mots d'anglais : le tour repart au modèle, même
si l'étape était mécanique. Une phrase scriptée ne sait que poser sa question.
**Où :** code — `learner_spoke_freely`
**Pourquoi :** c'est aussi le seul chemin qui reste aux outils (29) — tous se
déclenchent sur quelque chose que l'apprenant a dit.
**Changer :** `tutor.py` → `FREE_SPEECH_WORDS` (3)

### 4c-bis. Et l'étape n'est pas consommée — deux fois au plus
Le tour répond à l'apprenant, puis la leçon **revient à la même étape**. Au
troisième passage elle avance quand même.
**Où :** code — `MAX_STEP_WAITS` (2), le compteur `waits` de la leçon
**Pourquoi :** le tour repartait bien au modèle, mais l'étape était comptée
comme faite. Séance réelle : « I have a question. I don't understand
Tentoylannam. » — la question a reçu sa réponse, l'étape a été notée manquée, et
le tuteur a enchaîné sur un mot sans rapport. Rendre la main sans garder sa place
revient à punir celui qui pose une question.
**Pourquoi un plafond :** sans lui, quelqu'un qui bavarde ne quitte jamais la
première étape. Deux attentes, puis la leçon avance.
**Changer :** `tutor.py` → `MAX_STEP_WAITS`

### 4d. Le tour d'ouverture appartient toujours au modèle
Quoi qu'en dise le plan. Avec `--no-intro` un item est déjà chargé, et sa
première étape ouvrirait la séance par une question sèche à quelqu'un qui vient
de dire bonjour.
**Où :** code — `_conversation_loop`, `turns_done > 0`

### 5. Un tour se termine à sa question
Une question, puis le silence. Jamais répondre à sa propre question.
**Où :** prompt — THREE RULES
**Changer :** `persona.toml` → règle 2

### 6. Trois phrases maximum
Après le tour d'ouverture. L'apprenant doit parler au moins autant que le
tuteur.
**Où :** prompt — THREE RULES
**Changer :** `persona.toml` → règle 3

### 7. Une réponse est plafonnée à 500 tokens, raisonnement au minimum
Sans plafond, le modèle raisonnait sur un canal caché jusqu'à épuiser son
budget, et ne disait rien du tout.
**Où :** code
**Changer :** `tutor.py` → `MAX_TOKENS_PER_TURN`, `reasoning_effort`

---

## L'ordre du cours

### 8. La séquence est composée, jamais choisie
Les items sont enseignés dans l'ordre du roster. Le modèle ne choisit jamais
ce qui vient après et n'invente jamais un item.
**Où :** code — `select_new` renvoie l'ordre du roster, `pick_next_index` sert
**Changer :** l'ordre des items dans `content/vietnamese/*.toml`

### 9. Une phrase n'arrive jamais avant ses mots
`tôi tên là` ne peut pas être enseigné avant `tôi`, `tên` et `là`.
**Où :** code — `pick_next_index` saute un item dont les `pieces` manquent
**Pourquoi :** une session s'était ouverte sur une phrase de cinq mots dont
aucun n'avait été enseigné
**Changer :** `content.py` → `pick_next_index`, et le champ `pieces` des items

### 9b. La grammaire est espacée, jamais empilée
Après un trait, **quatre items** doivent passer avant qu'un autre puisse
venir. Et jamais plus de **trois items de la même catégorie** à la suite.
Personne n'est jeté : celui qui ne peut pas venir attend son tour.
**Où :** code — `MIN_ITEMS_BETWEEN_FEATURES` (4), `MAX_SAME_CATEGORY_RUN` (3), mais
la garantie dépend du champ `category` **écrit dans le contenu**
**Pourquoi :** un fichier porte un sujet et l'ordre des fichiers est l'ordre
d'enseignement, donc un fichier entier sort en bloc. Mesuré : **neuf traits
d'affilée** autour de l'item 35 — neuf minutes de théorie sans un mot nouveau.
Puis, après l'écriture du système de numération, **onze numéraux en onze places
consécutives** : un quart d'heure à compter et rien d'autre.
**Pourquoi dans le code et pas à la main :** espacer à la main ne survit pas à
2000 mots.
**Ce que ça exige du contenu :** une `category` juste sur chaque item. Une
catégorie fausse ou vide rend l'espacement aveugle sur cet item.
**Changer :** `content.py` → `MIN_ITEMS_BETWEEN_FEATURES`, `MAX_SAME_CATEGORY_RUN`

### 9c. Un trait qui nomme son mot passe devant l'espacement
Le champ `after` porte le nom d'un mot. Tant que ce mot n'est pas enseigné, le
trait attend ; dès qu'il l'est, le trait passe **avant toutes les règles
d'espacement**, 9b comprise.
**Où :** code — la branche `attached` de `pick_next_index` ; le champ `after`
est **écrit dans le contenu**, sur 13 des 35 traits
**Pourquoi contourner l'espacement :** l'espaceur existe pour empêcher les
traits de faire grappe. Un trait attaché à un mot ne fait pas grappe — il
**finit** le mot. Le contournement est l'intention du champ, pas un effet de
bord.
**Changer :** le champ `after` des items ; `content.py` → `pick_next_index`

## Ce que le cours sait

### 10. Chaque item porte ses propres données d'enseignement
`gloss` (« I / me »), `kind` (atome ou construction), `pieces`, `literal`.
**Où :** contenu — écrit à la main, pas déduit
**Pourquoi :** le code découpait le nom vietnamien en mots et se trompait dans
les deux sens — « cà phê » passait pour un assemblage, une règle de grammaire
pour une phrase. Et sans gloss, « demande ce qu'était là » sortait en « so how
would you say là ? » : une question qui donne sa réponse.
**Le `gloss` est maintenant prononcé tel quel** sur les tours scriptés (4b), sans
modèle entre lui et la synthèse : `speakable` traduit ce qui s'écrit mais ne se
dit pas — « I / me » → « I or me », « My name is ___ » → « My name is
something ». Et `check_roster` refuse qu'un item porte son propre nom
vietnamien dans son gloss, ce qui rendrait la réponse au moment de la question.
**Le repli assumé, et son risque :** quand un item n'a pas de gloss, deux
endroits retombent sur `description` — les notes d'écriture, rédigées **en
vietnamien** pour qui rédige le contenu. Aucun item enseigné n'a de gloss vide
aujourd'hui, donc rien ne le déclenche. Mais c'est la forme latente d'un défaut
déjà corrigé une fois ailleurs : `_lesson_note` ouvrait chaque tour sur cette
même description, et des fragments de vietnamien ressortaient au milieu de
phrases qui devaient être anglaises.
**Ce qui est porté mais jamais lu :** `type` (`concept`/`procedure`) sur les 2085
items, `senses` et `frequency_rank` sur les 1915 du stock. Aucun ne pilote une
décision d'enseignement — les garder ne coûte rien, s'y fier serait une erreur.
**Changer :** les fichiers d'items ; `fill_item_metadata.py` remplit les champs
manquants ; `tutor.py` → `speakable`, `_ask_for`

### 10b. Le cours sait qui est l'apprenant, et lui enseigne SES mots de personne
Une tranche d'âge et un genre suffisent : ils décident si l'apprenant est `anh`,
`chị` ou `em` face à quelqu'un. Le profil fournit les situations d'adresse
utilisées par la variation (12d) et par les traits d'adresse (13d) — et à
défaut de profil, le code retombe sur les situations que le cours enseigne.
**Où :** code — `learner.py`, `learner.json`, lu par `build_plan`
**Pourquoi :** le cours enseignait `tôi`, dont sa propre fiche dit *« đúng ngữ
pháp nhưng lạnh »* — grammaticalement juste, mais froid. Puis `anh`/`chị`/`em`
dans l'abstrait, comme un tableau à mémoriser. Dès que le cours sait qui vous
êtes, ce n'est plus une règle : ce sont **vos** mots.
**La limite assumée :** l'adresse dépend des DEUX personnes. Savoir qui est
l'apprenant est nécessaire, pas suffisant — mais « avec quelqu'un de plus jeune,
vous êtes `anh` » est déjà infiniment plus concret que la règle générale.
**Changer :** `learner.py` → `SELF_WHEN_OLDER`, `pair_with_minh`, `address_rows`

## Enseigner un mot

### 11. Un mot nouveau a deux tours
`introduce` puis `settle` — révélé et entendu, puis on réagit et on redemande.
**Où :** code — `build_plan`
**Pourquoi :** avec un seul tour chacun, trois mots défilaient en moins d'une
minute et aucun ne se posait
**Changer :** `tutor.py` → `build_plan`

### 11b. Un mot n'est jamais révélé sans son sens dans la même phrase
« In Vietnamese, the word for *name* is **tên**. » — le sens et le mot d'un
souffle, la phrase se termine sur le mot (donc Minh le dit), il est répété, puis
on demande de le dire.
**Où :** code — `_INTRODUCE`, composé par `scripted_turn`
**Pourquoi :** c'était une consigne, et elle a lâché. Séance réelle : chargé
d'introduire « tên », le modèle a dit « I didn't catch that », fait dire le mot
par Minh, puis demandé le mot. **La phrase qui donne le sens n'a jamais été
prononcée.** Un premier contact avec un mot sans son sens n'est pas une leçon.
**Ce qu'on perd :** la phrase de contexte optionnelle (« seulement si tu as un
vrai fait à raconter »). Elle n'a été produite **zéro fois** sur toutes les
séances enregistrées — on payait la garantie du tour pour un ornement jamais
livré.
**Changer :** `tutor.py` → `_INTRODUCE`

### 11c. Un fait vrai sur le mot passe DEVANT sa présentation
Quand un item porte un `hook`, il est dit en premier, puis la phrase qui donne
le mot. Le fait gagne le mot, puis le mot tombe.
**Où :** code — `scripted_turn` place `step.hook` en tête ; le `hook` lui-même
est **écrit dans le contenu**, un item à la fois
**Pourquoi devant et pas derrière :** sur `phở` ou `cà phê`, la phrase de
présentation seule tourne à vide — elle annonce à quelqu'un qui connaît déjà la
chose que le mot vietnamien est celui qu'il s'apprête à entendre.
**Ce que ça exige du contenu :** un fait **vrai**. La consigne d'annotation dit
« ne devine jamais » ; une étymologie inventée prononcée à voix haute est pire
que pas de hook du tout. Aujourd'hui un seul item du cours en porte un.
**Changer :** le champ `hook` des items ; `fill_item_metadata.py` pour la
consigne qui les fait écrire

## Enseigner une construction

### 12. Une construction déroule toute la chaîne
Un rappel par pièce, un par tour, puis l'ordre littéral, puis la réponse, puis
les variations, puis la règle énoncée en dernier.
**Où :** code — `build_plan`
**Changer :** `tutor.py` → `build_plan`, `N_VARIATIONS`

Les étoiles marquent les tours que le code écrit lui-même (4b) ; les autres
partent au modèle.

```
atome         introduce* -> settle* -> rapidfire* x3      (entièrement scripté)
construction  recall_piece* (un par piece) -> scaffold -> answer
              -> vary x2 -> rule -> rapidfire* x3
```

Un mot simple ne passe donc plus par le modèle du tout. Il garde la chaîne de
construction — échafaudage, variations, règle — et tout tour où l'apprenant
parle vraiment (4c).

### 12b. Un tour qui demande une réponse et la donne est signalé
Détection seulement : la réponse est streamée et parlée au fil de l'eau, donc
quand on peut juger, c'est déjà entendu. Ce qu'on gagne, c'est de le savoir.
**Où :** code — `_leaked_target`, sur les tours du modèle uniquement
**Le placeholder était le trou dans le garde-fou :** la cible d'une
construction est `tôi tên là + [tên riêng]`, et personne ne prononce jamais
« plus crochet tên riêng ». La comparaison littérale ne pouvait donc **jamais**
correspondre — le garde-fou n'a pas pu se déclencher une seule fois sur une
construction depuis qu'il existe, et « Tôi tên là Nam. » dit sur une étape qui
l'interdit est passé sans un mot dans les logs. On compare maintenant les
fragments réellement prononcés, tous requis.
**Changer :** `tutor.py` → `_PLACEHOLDER`, `_target_fragments`

### 12c. Une variation change la personne, pas seulement le mot du trou
« tôi tên là Nam » → « bạn tên là… ». Échanger le prénom ne teste rien ;
changer la personne teste si le motif a été compris.
**Où :** prompt — l'instruction de `vary`, construite par `build_plan` à partir
du `gloss` et du `literal` de l'item
**Pourquoi ça reste au modèle :** pour échanger `tôi` contre `bạn`, le code
devrait savoir que ces deux-là occupent la même place. `pieces` ne le dit pas,
et la catégorie non plus — `function_word` contient aussi « gì » et « chào », on
y tirerait « chào tên là ». Cette connaissance-là est du vietnamien : c'est ce
que le modèle a et qu'une table n'a pas. L'inverse exact des rappels, où le code
savait tout et le modèle dérivait.
**Ce que l'instruction fournit :** le périmètre, pas les mots — la phrase
(`gloss`), sa forme figée (`literal`), ce qui a le droit de bouger, et le
silence de Minh.
**Pourquoi elle a été réécrite :** l'ancienne disait « same structure, one
element swapped » et rien d'autre. Séance réelle : le modèle a retiré « tên » de
« tôi tên là » pour produire « tôi là », puis a interrogé sur « I am ___ ». Ce
n'était pas du bruit — c'était la bonne *sorte* de variation, sur une autre
phrase que celle enseignée. Rien ne lui avait dit ce qui devait rester.
**Changer :** `tutor.py` → `build_plan`, branche `vary`

### 12d. Une phrase qui contient une personne se fait varier PAR interlocuteur
`tôi tên là` et `bạn tên là gì?` portent un terme d'adresse. Leur variation
n'est pas « échange un mot » mais « dis-le à quelqu'un d'autre », et l'étape
nomme la situation à voix haute.
**Où :** code — `has_person_slot` détecte, `address_situations` fournit les
quatre lignes, l'instruction de `vary` les transmet
**La table était déjà dans le contenu** : la règle `cách chọn từ xưng hô` porte
ses quatre situations dans un champ `steps` que `Item` **ne chargeait pas**. La
donnée existait, personne ne pouvait la lire — donc le modèle réinventait, et il
a proposé « your name is » (donc `bạn`) un item avant que le cours l'enseigne.
**Trouvée par le contenu, pas par le nom :** est la règle d'adresse celle qui
porte des `steps` mentionnant un terme d'adresse. Coder le nom de l'item aurait
cassé au premier remaniement du contenu — il y en a eu deux aujourd'hui.
**Changer :** `content.py` → `ADDRESS_TERMS`, le champ `steps` des items

### 13. La règle est nommée après que le motif a été produit, jamais avant
**Où :** le code place l'étape en dernier ; le prompt dit comment la formuler
**Changer :** `tutor.py` → `build_plan`

*(Le mot « règle » ici désigne l'étape qui énonce le motif à la fin d'une
construction — l'étape `rule` du plan. Le **type d'item** ne s'appelle plus
ainsi : c'est `feature`, voir les traits ci-dessous.)*

---

## Enseigner un trait

Le troisième type d'item, à côté du mot isolé (11) et de la construction (12).
**35 items du cours**, deuxième type le plus nombreux. Ce ne sont ni des mots ni
des phrases : l'ordre sujet-verbe-objet, le fait qu'un verbe ne se conjugue
jamais, `ạ` qui rend poli n'importe quoi, les tons qu'on écoute et qu'on imite,
la politesse qui vit dans le mot de personne et non dans le ton de voix.

**Nom dans le code :** `kind = "feature"` — un **trait typologique**, au sens
où l'atlas WALS les catalogue. Leur nature s'écrit `nature = "discrete"` ou
`"strand"`. Voir `LEXIQUE.md`.

### 13b. Un trait fait redire ses pièces une à une, puis les assemble
La même forme qu'une construction : un rappel par pièce (jusqu'à
`MAX_FEATURE_PIECE_RECALLS`, 3), puis **une** étape d'application qui demande de
les mettre ensemble.
**Où :** code — la branche `item.kind == "rule"` de `build_plan`
**Pourquoi :** un trait n'avait qu'UN tour, qui devait énoncer la chose,
l'illustrer et l'appliquer d'un seul souffle — puis le plan enchaînait sur des
rappels sans rapport. Séquencement mesuré : trait → rapidfire `anh` →
rapidfire `em` → rapidfire `tên`. Énoncé une fois et plus jamais utilisé, ce qui
est exactement ce qu'un apprenant a rapporté : « je n'ai rien compris à la
règle, et elle n'est même pas utilisée ». Tous les autres types ont plusieurs
tours sur la chose enseignée ; celui-là était seul à n'en avoir qu'un.
**Effet de bord voulu :** les rappels de pièces sont scriptés (4b), donc deux
des trois tours de pratique d'un trait ne passent plus par le modèle.
**Changer :** `tutor.py` → `MAX_FEATURE_PIECE_RECALLS`, la branche `feature`

### 13c. Le code choisit la phrase sur laquelle un trait s'applique
Parmi les constructions déjà enseignées, celle qui partage **le plus de pièces**
avec le trait. Aucune ne partage : ce sont les mots propres du trait qui
servent de matière. Il n'en a pas : la liste des phrases connues, et le modèle
en choisit une.
**Où :** code — le tri `related`, par nombre de pièces communes décroissant
**Pourquoi ce n'est pas au modèle :** demander « une phrase différente » était
une consigne, et elle a été ignorée trois tours de suite — le tour du trait a
demandé « how would you answer Bạn muốn ăn ? », puis les deux applications ont
redemandé exactement la même. L'apprenant a entendu une question quatre fois et
la séance s'est terminée là. Que deux phrases soient différentes n'est pas un
jugement, donc ce n'est pas au modèle de le rendre.
**Pourquoi « le plus », et pas « la première » :** le trait des questions
oui/non (`có`, `không`) était épinglé sur `không phải là + [danh từ]`, qui ne
partage que `không` et parle de négation — les trois applications ont demandé
« pas étudiant » pendant qu'on enseignait comment poser une question. La
construction qui partageait les deux pièces attendait plus loin dans le cours.
**Pourquoi les mots propres en repli :** sans phrase partagée, on a tendu la
liste au modèle — et pour montrer qu'un adjectif se passe de `là`, il a choisi
« je ne suis pas étudiant », un nom, qui EXIGE `là`. L'application démontrait
l'inverse de ce qu'elle enseignait. Nommer les mots à assembler ne peut pas
faire ça.
**Changer :** `tutor.py` → la branche `feature`, le tri `related`

### 13d. Un trait qui porte SUR les mots d'adresse est posé comme une situation
Jamais comme une phrase. « Quelqu'un de plus âgé que toi, un homme — comment tu
lui dis ça ? » Trois échelons : la personne la plus facile, une tout autre, puis
une troisième où l'apprenant choisit lui-même le mot de personne. **Aucun
vietnamien n'est prononcé** : le nommer, c'est donner toute la réponse.
**Où :** code — `about_address`, puis trois étapes `apply` et un retour immédiat
**Pourquoi :** « How would you say anh ấy ? » — la question qui énonce sa
réponse. Les deux traits concernés, `ấy` et `ơi`, avaient le même défaut.
**Pourquoi un test étroit :** « contient un mot de personne » était trop
large — l'ordre des mots (`tôi, uống, cà phê`) et la possession (`của, cà phê,
tôi`) en utilisent un comme simple matière d'exemple sans porter dessus. Ils
auraient été demandés comme « appelle ce genre de personne », ce qui n'a aucun
sens. Le test est donc : **au moins deux** pièces d'adresse, **et** la moitié au
moins des pièces. Un seul mot de personne est un exemple, pas un sujet — c'est
ce que fait `tôi, là` dans le trait des tons.
**Ce que ça coûte :** ce chemin sort du plan immédiatement. Un trait
d'adresse n'a donc ni rappels de pièces (13b) ni rappels de clôture (17).
**Les situations viennent du profil de l'apprenant**, pas d'une table figée.
**Changer :** `tutor.py` → `about_address`, `ADDRESS_TERMS` dans `content.py`

---

## Comment les mots reviennent

### 14. Chaque mot porte un niveau
Niveau 0 à l'introduction, +1 à chaque rappel. La chance d'être tiré vaut
`1/(niveau+1)^1.5` — constante au début, rare ensuite, jamais nulle.
**Où :** code — `srs.weight`, `srs.draw_recalls`
**Pourquoi :** mesuré sur le cours de référence, rien n'est jamais « acquis »
puis retiré ; un mot apparaît simplement de moins en moins
**Changer :** `srs.py` → `DECAY`

### 15. L'espacement se compte en mots rencontrés, jamais en jours
Le cours est une ligne continue qu'on interrompt et qu'on reprend. Trente items
d'un trait ou étalés sur un mois donnent la même leçon.
**Où :** code — rien nulle part n'enregistre de date
**Changer :** `srs.py`

### 16. Les mauvaises réponses ne sont pas comptées
Un mot raté a besoin de plus d'exposition, ce qu'un niveau bas organise déjà.
**Où :** code — `record_recall` ne fait qu'incrémenter
**Changer :** `srs.py` → `record_recall`

### 17. Des rappels isolés closent presque chaque item — en nombre variable
Tirés par niveau, en excluant l'item qu'on vient d'enseigner et ses pièces.
Leur **nombre** varie de 1 à 4 : une base qui suit ce que l'item vient de faire
dire, plus ou moins un.
**Où :** code — `rapidfire_count`
**Pourquoi variable :** fixé à trois, chaque mot simple coûtait exactement cinq
tours, et un apprenant attentif apprend la cadence — après le deuxième rappel il
en reste un. Il répond au rythme et non à la question. `draw_recalls` refuse
déjà d'être prévisible sur QUELS mots reviennent ; le même argument n'avait
jamais été appliqué à COMBIEN.
**Pourquoi motivé et non aléatoire :** la base répond à une seule question — cet
item vient-il déjà de faire parler l'apprenant ? Une construction a fait redire
chacune de ses pièces, donc la révision est faite : en empiler trois de plus est
de la répétition sans objet (**1** avec pièces, **2** sans). Une règle fait
redire les siennes avant de les assembler, donc pareil (**2**). Un mot isolé n'a
rien révisé (**3**) — et c'est aussi la moyenne mesurée sur le cours de
référence.
**Ce que le 2 de la règle corrige :** elle valait 4, du temps où elle ne faisait
rien dire du tout. Depuis qu'elle porte ses propres rappels et ses applications,
quatre rappels étrangers par-dessus en faisaient l'item le plus long du cours
sans rien apprendre de plus.
**L'exception :** un trait d'adresse (13d) n'en reçoit aucun — son plan
s'arrête à ses trois situations.
**Ce que ça ne change PAS :** combien de fois un mot donné est révisé. Les
rappels d'un item portent sur d'AUTRES mots — l'item en cours est exclu. Un mot
revient par le plan des items suivants, tiré par niveau, indéfiniment (14).
**Changer :** `tutor.py` → `rapidfire_count`, où les quatre bases sont écrites en
dur. **Pas** `N_RAPIDFIRE` : cette constante ne porte plus que le défaut de
`_recall_targets`, que seul le smoke test emprunte — la séance, elle, passe
toujours le nombre calculé.

---

## Les réponses

### 18. Le mouvement central est « how would you say ___ ? », jamais « répète après moi »
L'apprenant construit à partir de pièces qu'il a. Seul un mot tout neuf est
répété tel quel.
**Où :** prompt — THE CORE MOVE
**Pourquoi :** « repeat after me » apparaît zéro fois en vingt-cinq minutes du
cours de référence ; « how would you say » apparaît vingt-deux fois
**Changer :** `persona.toml` → THE CORE MOVE

### 18b. Redemander le même mot se dit court, et marqué comme une reprise
« Et encore une fois, c'était quoi *I or me* ? » — pas la question complète une
seconde fois. Quatre formulations tournent, jamais deux fois la même d'affilée.
**Où :** code — `_REPEAT_ASK`, phrase composée par `scripted_turn` (4b)
**Pourquoi :** trois fois « What's the Vietnamese word for I or me ? » d'affilée
sonne comme trois questions différentes, et l'apprenant cherche ce qu'il a raté.
C'est aussi la signature du cours de référence : « and again, what was ___ ? »
y revient vingt et une fois.
**Changer :** `tutor.py` → `_REPEAT_ASK`, `_pick`

### 18c. Le tuteur apprend du code si la réponse était bonne
Le verdict est calculé par le code, puis transmis au modèle avec la consigne du
tour suivant : « correct », « raté deux fois », ou rien.
**Où :** code — `lesson["verdict"]`, lu par `_lesson_note` (tour du modèle) ou
par `_acknowledgement` (tour scripté, où il devient les premiers mots dits)
**Pourquoi :** sans ça le modèle rejuge tout seul à partir de la transcription
brute et contredit le code. Vu en session : trois tours de suite où le niveau
du mot montait et où le tuteur disait « I didn't catch that » dans le même
souffle.
**Ce que le tour scripté en dit, mot pour mot :** sur un mot **raté deux fois**,
le vietnamien est redonné — « It was ngon. » — dans sa forme prononçable, la même
que la relance. Sur une **bonne réponse**, une félicitation nue : « That's it. »,
« Exactly. » — **le mot n'est pas redit**. Et jamais rien du tout si la question
qui suit demande précisément ce mot : c'est la garde anti-fuite qui tranche, pas
une seconde règle écrite à côté.
**Changer :** `tutor.py` → `_lesson_note`, `_acknowledgement`, `_ACK_CORRECT`

### 19b. Une seule lettre, ou une seule lettre commune, ne suffit pas
En dessous de trois lettres, la cible exige une correspondance plus serrée
(0,60), et une réponse d'un seul caractère est refusée quel que soit son score.
**Où :** code — `SHORT_TARGET_LETTERS`, `SHORT_TARGET_THRESHOLD`
**Pourquoi :** `difflib` est grossier sur les chaînes courtes. Face à un mot de
deux lettres, en partager UNE score exactement 0,50 et franchit le seuil. Vu en
séance : « Dạ » accepté pour « là », niveau poussé à 7 — l'apprenant avait dit
autre chose et le mot a été enregistré comme consolidé. Et « D » valait « đi »,
au même score qu'un vrai « Đôi » pour « tôi ».
**Le seuil est placé dans l'écart, pas à son bord :** 0,50 doit échouer, 0,667
doit passer. 0,67 refusait « Đôi » d'un cheveu.
**Changer :** `tutor.py` → `SHORT_TARGET_THRESHOLD`

### 19. Une réponse reconnaissable est correcte
« Toi » pour tôi, un accent manquant, une transcription approximative : tout
cela est juste. On confirme et on avance. Jamais reposer la question qu'on
vient de poser.
**Où :** les deux — `answered_target` décide, le prompt donne le ton
**Changer :** `tutor.py` → `ANSWER_MATCH_THRESHOLD` (0.5)

### 20. Un mot vraiment différent a droit à une seule seconde chance
Minh le redit, la question est reposée court, puis la leçon avance quelle que
soit la réponse.
**Où :** code de bout en bout — `_should_retry` décide, `scripted_turn` écrit
la phrase (« Listen again — tôi. And again? »)
**Changer :** `tutor.py` → `_should_retry`, `_RETRY_ASK`

> **Faible, connu.** La reprise fait dire le mot par Minh puis le redemande :
> la réponse est donnée avant la question. La bonne forme serait plutôt
> « c'était tôi, répète après Minh » — assumer le raté au lieu de mettre en
> scène une question. C'était une consigne que le modèle interprétait ; c'est
> maintenant une seule ligne de code, donc une seule ligne à changer.

### 21. Tout vietnamien correct compte, pas seulement la formulation de l'item
« tên tôi là Nam » n'est pas corrigé en « tôi tên là Nam ».
**Où :** prompt — WHEN THEY GET IT WRONG
**Changer :** `persona.toml`

### 22. Une vraie question rejoue l'étape au lieu de la consommer
Pour qu'un plan scripté ne puisse pas rouler sur l'apprenant.
**Où :** code — `learner_asked_something`
**Changer :** `tutor.py`

---

## Entendre l'apprenant

### 23. L'enregistrement est mains libres
Démarre à la parole, s'arrête après 1,2 s de silence. Aucune touche, jamais.
**Où :** code
**Changer :** `listen.py` → `TRAILING_SILENCE_MS`

### 23b. Une trame est de la parole si le détecteur ET le volume sont d'accord
Le seuil de volume se mesure en continu — le 20ᵉ centile des trois dernières
secondes est le bruit de la pièce, et il faut le dépasser d'un facteur trois.
**Où :** code — `_speech_threshold`, dans le callback d'enregistrement
**Pourquoi :** mesuré sur un portable au ventilateur bruyant, `webrtcvad` au
maximum de sévérité classait **93 % du silence** comme de la parole, contre
91 % pour un mot prononcé — le silence marquait plus haut que la voix. Le même
enregistrement se séparait proprement au volume : 286 rms pour la pièce, 1117
pour le mot, des crêtes à 15× d'écart. Chacun est aveugle à une famille de
bruit différente : le ventilateur passe le détecteur mais pas le volume, une
porte qui claque passe le volume mais pas le détecteur.
**Pourquoi mesuré et non fixe :** un seuil calibré sur une pièce rendrait
l'app sourde dans une autre. La parole est la minorité bruyante des trames
récentes, donc un centile bas d'entre elles donne la pièce elle-même.
**Changer :** `listen.py` → `ENERGY_RATIO`, `ENERGY_ABSOLUTE_MIN`

### 24. Le silence est rogné avant l'envoi
La transcription Groq n'a pas de filtre de silence côté serveur, et Whisper
invente des phrases entières à partir de quasi-silence.
**Où :** code — `_trim_to_speech`
**Changer :** `listen.py` → `TRIM_PADDING_FRAMES`

### 24b. En dessous de cinq trames de parole, rien n'est envoyé du tout
Rogner ne suffit pas : le padding construit une fenêtre de 630 ms autour d'une
seule trame, et une trame isolée n'est pas un mot. On rend une transcription
vide, la boucle réécoute sans consommer l'étape.
**Où :** code — `MIN_SPEECH_FRAMES`, dans `record_until_silence`
**Pourquoi :** Whisper ne rend pas le vide sur du silence, il invente. Vu en
séance à 1 trame sur 126 : « ありがとうございました » — l'hallucination la plus
courante de Whisper, apprise sur des fins de vidéos YouTube muettes. Le tuteur
l'a comptée comme un mot raté et a monté le niveau.
**Le seuil est mesuré :** une vraie réponse d'un mot donne 13 trames et plus
(« tôi » → 13/70, transcrit « Tua »). Cinq trames font 150 ms — loin sous
n'importe quelle syllabe, loin au-dessus du bruit qui hallucine.
**Changer :** `listen.py` → `MIN_SPEECH_FRAMES`

### 25. La transcription sait quel mot elle attend
Quand l'étape en cours demande un rappel, une première passe en détection
automatique ; si elle ne rend pas le mot attendu, une seconde passe en forçant
le vietnamien. Une requête de plus uniquement quand la première échoue.
**Où :** code — `transcribe(expected=..., matches=...)`
**Pourquoi :** Whisper entend juste et écrit faux. `tên` sonne comme *ten* en
anglais, et il l'a transcrit **`10`** — le bon son, un texte inutilisable.
**Si la seconde passe ne rend pas le mot non plus**, on garde le texte de la
première — sauf si elle avait décodé dans une langue hors {vi, en}, auquel cas
c'est la passe forcée qu'on garde. Sinon le tag ment sur son propre texte : vu
en séance, une tentative de « tôi » arrivée en japonais sous une étiquette
`[lang:vi]`.

> **Et la seconde passe ne part JAMAIS sur une phrase anglaise.** La règle 25b
> s'applique aussi ici : plus de trois mots en anglais assuré, c'est l'apprenant
> qui nous parle, pas une tentative de mot. On garde ce qu'il a dit.
>
> **Pourquoi :** le pire échec produit par ce système. Étape attendant « tôi »,
> l'apprenant dit en anglais clair *« No, I'm asking for travel, listen, I don't
> care what I am me. »* Ça ne contient pas « tôi », donc passe forcée en
> vietnamien, qui rend *« Không, tôi đang chờ đề lý… »* — du vietnamien inventé
> qui contient « tôi » par hasard. Le seul test de récupération étant « est-ce
> que le mot attendu est dedans », l'invention a été acceptée, comptée comme
> bonne réponse, niveau monté, leçon avancée. L'apprenant protestait et s'est
> fait répondre « Exactly. »
>
> Se tromper dans l'autre sens est bon marché : une longue tentative
> vietnamienne prise pour de l'anglais est comptée ratée et redemandée. Se
> tromper dans ce sens-là **écrase ce que l'apprenant a réellement dit.**

**Changer :** `listen.py` → `is_learner_talking`, `transcribe`

### 25b. Quand rien n'est attendu, la longueur décide de la langue
Si la langue détectée sort de {vi, en} et qu'aucun mot n'est attendu : un ou
deux mots sont une tentative de vocabulaire, on force le vietnamien ; une
phrase est une question, on force l'anglais.
**Où :** code — `SENTENCE_WORDS`
**Pourquoi :** tout forcer en vietnamien a transformé « how do you say dog in
Vietnamese ? » en « Cái cách nói đáy ở Việt Nam ? », et le tuteur a enseigné le
mot pour « le fond ».
**Changer :** `listen.py` → `SENTENCE_WORDS`

### 26. La transcription n'est jamais réparée
Ce qui a été dit est ce que le tuteur voit.
**Où :** code — rien ne le fait, délibérément
**Pourquoi :** deux tentatives ont été faites et retirées. Un indice de
vocabulaire donné au décodeur faisait inventer du vietnamien à Whisper à partir
de bruit pur. Rapprocher le texte du mot connu le plus proche réparait la
mauvaise prononciation que le tuteur est justement censé entendre.

---

## L'ouverture

### 27. Trois points, une seule fois, tout au début
Dire les choses à voix haute ; ne pas chercher à retenir ; suivre le cours ou
demander son propre sujet. Puis Minh salue, puis une question, puis stop.
**Où :** les deux — le code décide *quand* (`lesson["started"]`), le prompt dit
quoi
**Pourquoi :** un plan vide voulait dire à la fois « pas commencé » et
« terminé », et le tuteur a ouvert une session neuve par « let's wrap up for
today »
**Changer :** `persona.toml` → OPENING

> **Coût connu.** 55 secondes de synthèse avant qu'il se passe quoi que ce
> soit. `--no-intro` la saute pendant qu'on travaille sur la leçon elle-même.

---

## La prononciation

### 28. Le tuteur ne juge jamais comment l'apprenant sonne
Aucun verdict sur un son : ni sur un ton, ni sur une voyelle, ni sur rien de ce
qui a été dit. On réagit à **quel mot** c'était, jamais à comment il sonnait.
**Où :** prompt — NEVER JUDGE HOW THEY SOUND
**Pourquoi :** le tuteur n'entend jamais l'apprenant, seulement une
transcription approximative — tout verdict est une devinette, et il en
inventait de fausses (« tên » glosé « le a de bed »)
**Changer :** `persona.toml` → NEVER JUDGE HOW THEY SOUND

### 28b. Les tons SONT enseignés, comme n'importe quel item
Six règles ancrées sur des mots déjà connus (`06_thanh_dieu.toml`) : le signe
existe, il porte la hauteur, et son dessin est celui de la voix.
**Où :** contenu — les règles ; le prompt autorise seulement
**Historique :** le prompt interdisait *« ne nomme jamais un ton, n'explique
jamais que le vietnamien a des tons »*. C'était un échafaudage temporaire, posé
quand aucun contenu n'existait — pas une position pédagogique. Il est tombé avec
l'arrivée des règles, et l'esquive qui allait avec (« ça viendra plus tard »)
aussi : elle serait devenue un mensonge.
**Ce qui n'a pas bougé :** 28. Enseigner un ton et diagnostiquer un ton sont
deux choses ; seule la seconde est interdite, et elle l'est pour une raison qui
tient toujours.
**Changer :** `content/vietnamese/06_thanh_dieu.toml`

### 28c. Un mot qui ne diffère d'un ancien que par le ton se présente en paire
À l'introduction du **nouveau** mot seulement, et seulement si l'ancien est
connu : les deux sont dits par Minh l'un derrière l'autre, dans le même souffle.
`ba` puis `bà`, un seul clip, deux mots.
**Où :** code — `tone_twin` calcule, `_INTRODUCE_TWIN` prononce
**Pourquoi la paire :** le tuteur n'entend jamais l'apprenant (28), donc la seule
pédagogie honnête est de rendre la différence **audible**. Deux mots collés sont
le seul instant où la différence existe pour une oreille étrangère.
**Pourquoi au second seulement :** deux sosies enseignés côte à côte
s'entremêlent. Mesuré : presque 40 % du vocabulaire a un sosie, mais trois paires
seulement parmi les mots enseignés aujourd'hui — le mécanisme sert peu et
grandira avec le vocabulaire.
**Calculé, jamais annoté :** le ton est dans le diacritique.
**Changer :** `tutor.py` → `tone_twin`, `_INTRODUCE_TWIN`

---

## Les outils

### 29. Trois outils, tous rares
`set_session_focus` (l'apprenant demande un thème, quatre items sont générés),
`remember_word` (il demande comment dire quelque chose hors programme),
`deprioritize_item` (il demande d'abandonner quelque chose — enterré au niveau
12, jamais supprimé).
**Où :** le code exécute, le prompt décide quand
**Portée :** uniquement sur les tours que le modèle écrit. Un tour scripté (4b)
ne passe par aucun modèle, donc par aucun outil — sans conséquence, puisque les
trois se déclenchent sur une demande explicite de l'apprenant, et que parler
rend justement la main au modèle (4c).
**Changer :** `tutor.py` → `TOOLS`

### 29b. Un outil qui échoue ne termine jamais la leçon
La génération de thème est encapsulée : si elle casse, on l'écrit dans les logs
et la séance continue sans le thème.
**Où :** code — le `try` autour de `generate_theme_items`
**Pourquoi :** la toute première fois que `set_session_focus` s'est déclenché,
la génération a rendu un 400, l'exception est remontée hors du gestionnaire
d'outil, et une séance par ailleurs saine est morte à son deuxième tour.
**Changer :** `tutor.py` → `_run_turn`

### 29c. La génération de thème n'est pas un tour parlé
Elle émet du JSON, pas de la parole, et a son propre plafond de jetons.
**Où :** code — `THEME_GENERATION_MAX_TOKENS` (2500) contre
`MAX_TOKENS_PER_TURN` (500)
**Pourquoi :** elle héritait du plafond des trois phrases parlées. Quatre items
avec leurs notes en vietnamien font quatre fois ça, le JSON sortait tronqué, et
Groq répondait 400 « tool_use_failed ». Une troncature n'est pas un résultat
dégradé, c'est un refus.
**Et le schéma accepte `null`** sur `pieces` et `literal` : ils sont documentés
« constructions uniquement », donc sur un atome le modèle écrit `null` — ce
qu'un schéma non-nullable transformait en 400, perdant le lot entier pour un
champ qui ne s'appliquait pas.

### 29d. Un refus définitif n'est pas réessayé
Un 4xx qui n'est pas 429 veut dire que la requête est fausse ; la répéter ne
peut pas aider.
**Où :** code — `PermanentAPIError`, `_permanent`
**Pourquoi :** le 400 ci-dessus a été renvoyé cinq fois avant de planter,
brûlant cinq fois le budget sur une requête qui ne pouvait pas aboutir.
**Changer :** `tutor.py` → `_permanent`

> **La génération produit des phrases entières**, que la règle 9 repoussera
> jusqu'à ce que leurs mots soient enseignés — peut-être indéfiniment.

---

## L'infrastructure

### 30. Un seul modèle, aucun secours
Sur un 429, le code attend et réessaie le même modèle.
**Où :** code
**Pourquoi :** toutes les alternatives cassent le format — l'une écrit ses
appels d'outils en texte que le tuteur lit à voix haute, l'une fuit ses jetons
internes dans les noms d'outils, l'une déclenche des outils sans rien dire
**Changer :** `tutor.py` → `MODEL`

### 31. Le budget est de 8000 tokens par minute
Mesuré, pas documenté. À ~3000 tokens la requête, cela fait environ deux
requêtes et demie par minute — c'est pour ça que le prompt système reste petit.
Depuis 4b, environ la moitié des tours n'envoie plus rien du tout.
**Où :** le palier gratuit de Groq
**Changer :** payer, ou réduire `persona.toml`

### 32. La progression s'écrit au fil de la session, et se relit dans l'ordre
Un plantage ne coûte rien. `--fresh` n'écrit rien du tout.

Et elle se **relit dans l'ordre où elle a été écrite**, pas dans celui du roster.
**Où :** code — `taught_order` lit le fichier d'état, la reprise s'en sert
**Pourquoi :** les contrôles d'espacement regardent les derniers items vus. Un
historique reconstruit dans l'ordre du roster les fait décider autrement que la
séance qui a produit l'état — `--at=120` ouvrait sur le mauvais item, et trois
traits sur sept manquaient le leur. Une partie de ce qui ressemblait à du
contenu qui dérive était l'état rebâti de travers avant le premier mot.
**Changer :** `tutor.py` → `run_session` ; `srs.py` → `taught_order`
