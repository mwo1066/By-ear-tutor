# Faire monter une construction, au lieu de la demander entière

**Statut :** proposé
**Ouvert le :** 2026-08-15

## Pourquoi

Le principe est déjà écrit dans le code, cité de Meo pendant un test :

> A rule is put to work by CLIMBING one sentence, not by being asked for whole
> sentences repeatedly. *« He always starts calm — how do you say don't want,
> then I don't want, then I don't want to eat. »*

Il n'est appliqué qu'à **une branche sur trois** :

| | monte ? |
| --- | --- |
| trait d'adresse | oui — trois barreaux |
| autre trait | non — une seule application |
| **construction** | **non** — l'ordre littéral entier, puis la phrase entière d'un coup |

Une construction dit aujourd'hui : *« voilà l'ordre mot à mot, maintenant dis
la phrase »*. Pour `tôi tên là + [tên riêng]`, c'est quatre mots demandés d'un
bloc à quelqu'un qui vient d'apprendre les trois pièces séparément.

## Ce qui change dans SPEC.md

La règle 12 décrit la chaîne d'une construction — « puis l'ordre littéral, puis
la réponse ». Elle devra dire que la phrase se **monte** : deux ou trois
barreaux, chacun ajoutant un élément, le dernier étant la phrase entière.

## Ce que le code ne peut pas savoir, et qui décide de la forme

**Quels sont les paliers valides d'une phrase est une connaissance de
vietnamien.** Le champ `pieces` donne les mots, pas les étapes : `tôi`, `tên`,
`là` ne dit pas que `tôi tên` n'est pas une phrase.

Donc les barreaux sont des **tours du modèle**, et le code fournit la frontière —
exactement la doctrine déjà écrite pour l'étape `vary` :

> Which element is swappable is the one thing the code cannot work out […] That
> knowledge is Vietnamese, which is exactly what the model has and a table does
> not. So this stays a model turn, and the instruction supplies the boundary.

Le code fournit : la phrase visée, ses pièces, la liste des mots enseignés, et la
règle « un élément de plus par barreau, on reste sur la même phrase ».

## Périmètre

**Dedans :**

- l'étape `scaffold` devient deux ou trois barreaux au lieu d'un tour
- l'ordre littéral est donné sur le **dernier** barreau, celui de la phrase
  entière — c'est là que l'ordre compte
- la garde `_known_words_note` est ajoutée, que l'échafaudage n'a pas
  aujourd'hui alors que `vary` et `apply` l'ont

**Dehors :**

- **les traits.** Leur branche a déjà sa forme, et la toucher doublerait le
  périmètre.
- **le nombre de variations et l'énoncé du motif**, qui ne bougent pas.
- **l'instruction menteuse quand `literal` est vide** — elle disparaît d'elle-même
  puisque l'ordre littéral se déplace sur le dernier barreau, où il est
  conditionnel.

## Deux décisions prises avant d'implémenter

**Le total de tours ne bouge pas.** Des barreaux ajoutent des tours, ce qui est
la direction inverse de « rendre une phrase bon marché ». Ils sont donc pris sur
le budget des variations :

```
aujourd'hui   échafaudage(1) + réponse(1) + variations(2)  =  4 tours produits
avec échelle  barreaux(2-3)  + réponse(1) + variations(1)  =  4 tours produits
```

C'est cohérent avec la méthode : chez Noble, **monter EST la variation**. « je
veux » → « je veux manger » → « je ne veux pas manger » n'est pas construire puis
varier, c'est le même geste.

**La garde des mots connus reste une consigne, et on l'assume.** Elle a deux
régimes : en dessous de douze mots enseignés elle **liste** le vocabulaire, au
delà elle dit seulement « n'introduis rien de neuf ». C'est du **prompt**, pas du
code — et c'est précisément pourquoi la règle `ở`, qui arrive à l'item 48, a
demandé « à la maison » malgré la consigne.

Une échelle demande plus au modèle qu'une variation, donc plus d'occasions de
déraper sous une garde faible. Décision de Meo : **on accepte et on écoute.** Le
filet — un contrôle après coup qui signale un tour prononçant un mot jamais
enseigné, sur le modèle de `_leaked_target` — vaut son propre dossier et ne doit
pas retarder ce qu'on veut entendre.

## Le risque, et il est réel

Un barreau inventé par le modèle peut demander un mot jamais enseigné — c'est
exactement ce qui est arrivé à la règle `ở` (« je suis à la maison, à l'école,
au marché », aucun des trois enseigné). La garde des mots connus est la
mitigation, et elle a déjà fait ses preuves sur `vary` et `apply`.

Il peut aussi produire un palier qui n'est pas une phrase (`tôi tên`).
L'instruction doit dire que **chaque barreau doit être une chose qu'on peut
dire**, pas un morceau.

## Ce qui ne se vérifie pas par un test

`smoke_test.py` verra que le plan a le bon nombre d'étapes et que rien ne fuit.
Il ne peut pas dire si les barreaux sont bien choisis — c'est du vietnamien et du
jugement pédagogique. **Ce changement doit être entendu en séance avant d'être
gardé.**

## Tâches

- [x] Remplacer l'étape `scaffold` unique par des barreaux
- [x] Donner l'ordre littéral sur le dernier barreau seulement
- [x] Ajouter `_known_words_note` à l'instruction
- [x] Exiger que chaque barreau soit une chose qu'on peut dire, pas un fragment
- [x] Modifier la règle 12 de `SPEC.md`
- [x] `python smoke_test.py`
- [x] **Écouter une séance** sur une construction — faite le 15 août, elle a trouvé un défaut
- [ ] **Réécouter** après correction du barreau 1, avant d'archiver

## Vérification

Compter les tours d'une construction avant et après, et lire les instructions
produites pour trois constructions de tailles différentes. Puis une séance
réelle : est-ce que les barreaux montent, ou est-ce que le modèle redemande
trois fois la même phrase ?

## Ce que l'écoute a trouvé

Séance réelle sur `tôi tên là + [tên riêng]`, plan `recall_piece ×3 → scaffold ×2
→ answer → vary → rule → rapidfire`. L'échelle a bien tourné.

**Le barreau 2 marche :** *« In Vietnamese the order is: I name is something.
Now — My name is something ? »*, et l'apprenant a répondu `Tôi tên là`.

**Le barreau 1 était cassé :** il a demandé *« What's the Vietnamese word for
"I" ? »* — c'est-à-dire `tôi`, **trois tours après le rappel qui venait de le
demander**. L'instruction disait « un élément de moins que le barreau suivant »,
et le modèle est descendu à un mot seul.

Corrigé : le plancher est **deux pièces assemblées**. Un mot seul répète le tour
d'avant au lieu de construire — chaque pièce vient d'être rappelée isolément
juste avant.

**Ce que l'écoute n'a pas pu juger**, parce que la séance a dérivé après :
l'apprenant a parlé librement, l'étape a attendu (4c-bis), et le modèle a pris la
main jusqu'à enseigner `sinh viên`, hors cours. Le plan n'a jamais repris. C'est
un défaut distinct, hors de ce dossier.
