# Ce que fait le tuteur

Chaque comportement en français, avec l'endroit où il est appliqué et ce qu'il
faut modifier pour le changer. Écrit à partir du code, pas de mémoire.

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

## Les deux voix

### 1. Deux locuteurs, aiguillés par la langue
Le tuteur parle la langue de l'apprenant, Minh uniquement le vietnamien. La
voix entendue est décidée par la langue dans laquelle chaque phrase est écrite
— le modèle ne pose aucune étiquette.
**Où :** code — `voice.split_by_voice` découpe mot par mot
**Changer :** `voice.py` → `TUTOR_VOICE`, `TEACHER_VOICE`

### 2. Les didascalies et le markdown sont supprimés
« Minh: » écrit comme une étiquette, ou `**gras**`, n'atteint jamais les
haut-parleurs.
**Où :** les deux — le prompt l'interdit, `voice._strip_markdown` le retire
quand même
**Pourquoi les deux :** le code empêche que ce soit *entendu*, seul le prompt
empêche le modèle de *penser* en listes à puces, ce qui aplatit la pédagogie
**Changer :** `voice.py` → `_SPEAKER_LABEL`, `_MARKDOWN_CHARS`

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

## Ce qui est enseigné, et dans quel ordre

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

### 10. Chaque item porte ses propres données d'enseignement
`gloss` (« I / me »), `kind` (atome ou construction), `pieces`, `literal`.
**Où :** contenu — écrit à la main, pas déduit
**Pourquoi :** le code découpait le nom vietnamien en mots et se trompait dans
les deux sens — « cà phê » passait pour un assemblage, une règle de grammaire
pour une phrase. Et sans gloss, « demande ce qu'était là » sortait en « so how
would you say là ? » : une question qui donne sa réponse.
**Changer :** les fichiers d'items ; `fill_item_metadata.py` remplit les champs
manquants

### 11. Un mot nouveau a deux tours
`introduce` puis `settle` — révélé et entendu, puis on réagit et on redemande.
**Où :** code — `build_plan`
**Pourquoi :** avec un seul tour chacun, trois mots défilaient en moins d'une
minute et aucun ne se posait
**Changer :** `tutor.py` → `build_plan`

### 12. Une construction déroule toute la chaîne
Un rappel par pièce, un par tour, puis l'ordre littéral, puis la réponse, puis
les variations, puis la règle énoncée en dernier.
**Où :** code — `build_plan`
**Changer :** `tutor.py` → `build_plan`, `N_VARIATIONS`

```
atome         introduce -> settle -> rapidfire x3
construction  recall_piece (un par piece) -> scaffold -> answer
              -> vary x2 -> rule -> rapidfire x3
```

### 13. La règle est nommée après que le motif a été produit, jamais avant
**Où :** le code place l'étape en dernier ; le prompt dit comment la formuler
**Changer :** `tutor.py` → `build_plan`

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

### 17. Trois rappels isolés closent chaque item
Tirés par niveau, en excluant l'item qu'on vient d'enseigner et ses pièces.
**Où :** code
**Changer :** `tutor.py` → `N_RAPIDFIRE`, `_recall_targets`

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
« Et encore une fois, c'était quoi *I / me* ? » — pas la question complète une
seconde fois.
**Où :** code — les consignes de `settle` et de la reprise
**Pourquoi :** trois fois « What's the Vietnamese word for I or me ? » d'affilée
sonne comme trois questions différentes, et l'apprenant cherche ce qu'il a raté.
C'est aussi la signature du cours de référence : « and again, what was ___ ? »
y revient vingt et une fois.
**Changer :** `tutor.py` → `build_plan`, `_lesson_note`

### 19. Une réponse reconnaissable est correcte
« Toi » pour tôi, un accent manquant, une transcription approximative : tout
cela est juste. On confirme et on avance. Jamais reposer la question qu'on
vient de poser.
**Où :** les deux — `answered_target` décide, le prompt donne le ton
**Changer :** `tutor.py` → `ANSWER_MATCH_THRESHOLD` (0.5)

### 20. Un mot vraiment différent a droit à une seule seconde chance
Minh le redit, la question est reposée autrement, puis la leçon avance quelle
que soit la réponse.
**Où :** le code décide (`_should_retry`), le prompt formule
**Changer :** `tutor.py` → `_should_retry`

> **Faible, connu.** La reprise fait dire le mot par Minh puis le redemande :
> la réponse est donnée avant la question. Un garde-fou dans le code le repère
> et l'écrit dans les logs, mais la consigne demande toujours ça. La bonne
> forme serait plutôt « c'était tôi, répète après Minh » — assumer le raté au
> lieu de mettre en scène une question.

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

### 25. Seuls le vietnamien et l'anglais sont acceptés
Tout le reste est re-transcrit en forçant le vietnamien.
**Où :** code — `ALLOWED_LANGUAGES`
**Pourquoi :** une tentative ratée de vietnamien revenait taguée français avec
du texte français, et le tuteur répondait en français au milieu de la leçon

> **Cassé, connu.** Une vraie question en anglais mal détectée comme du
> français est forcée en vietnamien et détruite. « How do you say dog in
> Vietnamese ? » est devenu « Cái cách nói đáy ở Việt Nam ? » et le tuteur a
> enseigné le mot pour « le fond ». La longueur est le discriminant gratuit :
> un ou deux mots, c'est une tentative ; une phrase, c'est une question.

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

### 28. La prononciation n'est pas enseignée, les tons ne sont pas mentionnés
Écouter Minh et copier. Aucun nom de ton, aucun conseil d'articulation, aucune
description de son.
**Où :** prompt — PRONUNCIATION
**Pourquoi :** le tuteur n'entend jamais l'apprenant, seulement une
transcription approximative — tout verdict est une devinette, et il en
inventait de fausses (« tên » glosé « le a de bed »)
**Changer :** `persona.toml` → PRONUNCIATION

---

## Les outils

### 29. Trois outils, tous rares
`set_session_focus` (l'apprenant demande un thème, quatre items sont générés),
`remember_word` (il demande comment dire quelque chose hors programme),
`deprioritize_item` (il demande d'abandonner quelque chose — enterré au niveau
12, jamais supprimé).
**Où :** le code exécute, le prompt décide quand
**Changer :** `tutor.py` → `TOOLS`

> **Jamais déclenché.** `set_session_focus` n'a tourné dans aucune session. Et
> la génération produit des phrases entières, que la règle 9 repoussera jusqu'à
> ce que leurs mots soient enseignés — peut-être indéfiniment.

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
**Où :** le palier gratuit de Groq
**Changer :** payer, ou réduire `persona.toml`

### 32. La progression s'écrit au fil de la session
Un plantage ne coûte rien. `--fresh` n'écrit rien du tout.
**Où :** code
**Changer :** `tutor.py` → `run_session`
