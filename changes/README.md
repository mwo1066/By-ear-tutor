# Les changements

`SPEC.md` dit ce que le tuteur fait **aujourd'hui**. Ici on écrit ce qu'on veut
qu'il fasse **ensuite** — avant d'y toucher.

- `changes/` — ce qui est proposé ou en cours. Un dossier par changement.
- `changes/archive/` — ce qui est fait. On n'y touche plus.
- `changes/archive/JOURNAL.md` — la liste complète, la plus récente en haut.
  **C'est le fichier qu'on lit avant de proposer quoi que ce soit.**

## Le rituel

| étape | commande | ce qui se passe |
| --- | --- | --- |
| **1. Proposer** | `/proposer <idée>` | Je lis le journal, je vérifie qu'on ne l'a pas déjà fait ou déjà défait, j'écris `changes/NNNN-nom/proposition.md`. **Aucun code n'est écrit.** Tu lis, tu corriges, tu refuses. |
| **2. Appliquer** | `/appliquer NNNN` | J'implémente les tâches dans l'ordre, en cochant. Si la réalité diverge de la proposition, je m'arrête et je te le dis — je ne dérive pas en silence. |
| **3. Archiver** | `/archiver NNNN` | Je replie le changement dans `SPEC.md`, j'écris ce que ça a donné, je déplace le dossier dans `archive/` et j'ajoute la ligne au journal. |
| **à part** | `/derive` | Je relis le code, je redérive les règles, et je liste ce que `SPEC.md` affirme et que le code ne fait plus. Je ne change rien. |

## Pourquoi avant, et pas après

Une spec écrite après le code décrit ce qui a été fait. Écrite avant, elle
décide ce qui sera fait — et c'est la seule version que tu peux refuser avant
qu'elle coûte quelque chose.

Rien ici n'est une garantie. C'est un rituel : il tient tant qu'on le suit.
La différence avec l'état d'avant, c'est qu'un rituel qu'on saute laisse une
trace — le dossier manquant, la ligne absente du journal.

## Un changement, un périmètre

**Le test : un changement répare *une* chose qu'une séance réelle pourrait
montrer de travers.** S'il faut deux observations distinctes pour le justifier,
c'est deux changements.

Signes qu'il faut découper, et je dois te le proposer quand je les vois :

- le « Pourquoi » ne s'écrit qu'avec un « et » entre deux problèmes ;
- deux moitiés des tâches pourraient être livrées séparément et chacune servir ;
- ça touche du **code** ici et du **prompt** là, pour des raisons sans rapport ;
- les règles de `SPEC.md` touchées ne sont pas dans la même section.

Découper coûte un dossier de plus. Ne pas découper coûte un changement qu'on ne
peut plus ni relire, ni refuser à moitié, ni retrouver dans le journal.

## Le gabarit

Un seul fichier par changement, `proposition.md` :

```markdown
# <Ce que ça change, en une ligne>

**Statut :** proposé
**Ouvert le :** AAAA-MM-JJ

## Pourquoi
Ce qui ne va pas, **observé**. Une séance, une sortie, une ligne de code —
pas une supposition.

## Ce qui change dans SPEC.md
Par numéro de règle, avec le verbe qui va bien :
- règle 12c — **modifiée** : ...
- règle 34 — **nouvelle** : ...
- règle 7 — **supprimée**, parce que ...

Et pour chaque règle, la ligne qui compte : **code** ou **prompt**.

## Périmètre
**Dedans :** ...
**Dehors :** ... (ce qu'on aurait pu y mettre et qu'on n'y met pas)

## Tâches
- [ ] ...

## Vérification
Comment on saura que c'est fait. `smoke_test.py` au minimum ; dis lequel des
cas il couvre, et ce qu'il ne couvre pas.
```

À l'archivage, une dernière section est ajoutée :

```markdown
## Résultat
**Terminé le :** AAAA-MM-JJ — commits `abc1234`, `def5678`

Ce qui a été fait autrement que prévu, et pourquoi. Ce qu'on a essayé et
abandonné en route. **C'est la section qui évite de le refaire dans six
semaines.**
```
