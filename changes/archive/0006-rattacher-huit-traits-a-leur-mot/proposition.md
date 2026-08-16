# Rattacher huit traits au mot dont ils parlent

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Le champ `after` nomme le mot avec lequel un trait va. Tant que ce mot n'est pas
enseigné, le trait attend ; dès qu'il l'est, le trait passe devant les règles
d'espacement (règle 9c). Sans `after`, un trait attend son tour dans la file,
et sa position ne dépend que du nombre de traits qui le précèdent.

Mesuré dans le code : **le trait médian arrive 47 items après le dernier de ses
propres mots, et 21 sur 30 attendent plus de 30 items.** L'apprenant rencontre un
mot, le travaille comme du vocabulaire, et apprend une heure plus tard où il se
place.

Treize traits portaient déjà un `after`. Vingt-deux ne l'avaient pas — et parmi
eux, huit nomment leur mot **dans leur propre titre**.

## Ce qui change dans SPEC.md

Rien. La règle 9c décrit déjà le mécanisme ; ceci remplit un champ de contenu.

## Périmètre

**Dedans :** huit champs `after` dans les fichiers de contenu.

| trait | mot | tier |
| --- | --- | --- |
| `phủ định: không + [...]` | `không` | 1 |
| `câu hỏi có/không` | `có` | 1 |
| `ạ: một chữ làm câu lịch sự` | `ạ` | 2 |
| `sở hữu: danh từ + của + người` | `của` | 2 |
| `được đứng sau động từ` | `được` | 3 |
| `cũng đứng trước động từ` | `cũng` | 3 |
| `rất trước, lắm sau` | `rất` | 3 |
| `so sánh: tính từ + hơn` | `hơn` | 3 |

**Dehors :**

- **sept traits `discrete` qui ne portent sur aucun mot** — l'ordre
  sujet-verbe-objet, l'absence de genre, l'adjectif après le nom. Rien à
  rattacher : ils parlent d'une forme, pas d'un mot.
- **les sept `strand`**, qui ne sont pas séquencés comme des items.

## Vérification, faite avant d'écrire

**Rattacher peut retarder** si le mot arrive après le trait. Simulé sur les huit
avant de toucher au contenu : aucun n'est retardé. C'est mécanique — un mot cité
dans le titre est aussi une pièce, et un item n'est jamais enseigné avant ses
pièces (règle 9).

**Effet mesuré**, même graine, `after` neutralisé puis actif :

```
écart entre un trait et son mot, pour les huit
   avant : médiane 46 items   (max 96)
   après : médiane  1 item    (max 15)
```

Le maximum reste à 15 parce que `after` ne court-circuite pas les prérequis :
`rất trước, lắm sau` attend aussi `lắm`, qui est une de ses pièces. C'est
correct — un trait ne peut pas arriver avant les mots dont il est fait.

## Tâches

- [x] Trouver les traits qui nomment leur mot sans le déclarer
- [x] Vérifier qu'aucun ne serait retardé
- [x] Écrire les huit champs `after`
- [x] Mesurer l'écart avant / après
- [x] `python smoke_test.py`

## Résultat

**Terminé le :** 2026-08-15 — huit items, cinq fichiers de contenu.

**Deux faux départs sur le tri, qui valent d'être notés.**

Le premier tri cherchait « un trait dont **une seule** pièce est un mot
enseigné ». Il n'a trouvé qu'un candidat sur vingt-deux, et rangeait `cũng đứng
trước động từ` parmi les cas légitimes — alors que son titre nomme `cũng`. Le bon
critère était « un mot enseigné qui apparaît **dans le titre et dans les
pièces** » : huit candidats, et aucun faux positif à l'inspection.

Le second : le script a rapporté **neuf** rattachements pour huit items modifiés.
La différence venait d'un nom de **construction** proche de celui d'un trait —
`câu hỏi có/không: có + [động từ] ... không?` contre `câu hỏi có/không`. La
recherche par fragment a touché les deux, l'insertion n'a eu lieu que sur le
trait, et le compteur a compté les deux. Sans le `git diff`, la mesure de
position qui a servi à décider portait sur la construction et non sur le trait.
**Un compteur qui ne compte pas ce qu'on croit est plus dangereux qu'une erreur
visible.**
