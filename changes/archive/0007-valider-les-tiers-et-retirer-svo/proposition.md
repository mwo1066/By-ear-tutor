# Valider le classement en tiers, et retirer l'ordre sujet–verbe–objet du cours

**Statut :** terminé
**Ouvert le :** 2026-08-15

## Pourquoi

Le classement des traits `discrete` en trois tiers d'utilité existait depuis le
matin du 15 août et **n'avait jamais été validé** — c'était la proposition d'un
assistant, jamais corrigée. Tant qu'il n'est pas validé, réordonner le cours
d'après lui est bloqué.

## Ce qui change dans SPEC.md

Rien. Le champ `tier` n'est encore lu par aucun code : il attend le
réordonnancement, qui est un autre changement.

## Trois décisions de Meo

**1. L'ordre sujet–verbe–objet sort du cours.** L'item est supprimé, pas
déclassé.

Sa propre fiche le présentait comme le filet du débutant — *« đây là chỗ dựa an
toàn cho người mới: khi chưa chắc, cứ xếp như tiếng Anh thì thường đúng »*, le
point d'appui sûr pour un débutant. C'est précisément l'argument contre :
**un francophone place déjà sujet, verbe, objet sans y penser.** La règle
occupait un créneau de leçon pour enseigner un réflexe acquis, et elle était en
tête du tier 1.

Vérifié avant suppression : aucun item ne la cite comme pièce ni comme `after`.
Le cours passe de 35 à 34 traits.

**2. `đã` monte en tier 1.** Le passé fait partie de ce sans quoi on ne peut pas
parler : c'est lui qui met de la variété dans les phrases, et l'apprendre tôt
ouvre tout ce qui suit.

**3. « Les verbes ne changent jamais » monte avec lui.** Elle était en tier 3,
classée comme confort, alors qu'elle **pose la question** à laquelle `đã` répond
— et elle s'explique en une phrase. Le raisonnement de Meo : on énonce la règle
simple, l'apprenant la comprend immédiatement, et on enchaîne sur le passé.

L'enchaînement obtenu, mesuré sur le séquencement réel :

```
25  đã                     le mot
26  động từ không chia     « les verbes ne changent jamais »
27  đã: việc đã xong       « voilà comment on dit le passé »
```

Les deux règles sont attachées au mot `đã`, donc elles arrivent ensemble. **Leur
ordre entre elles n'est pas garanti** : il vient de l'ordre des fichiers, et
`pick_next_index` prend le premier attaché qu'il trouve. Il se trouve qu'il est
bon. Si un remaniement de contenu l'inversait, l'apprenant recevrait la réponse
avant la question, et rien ne le signalerait.

## Périmètre

**Dedans :** la suppression de l'item SVO, deux champs `tier`, la section des
tiers dans `STYLE.md`.

**Dehors :**

- **`đang` et `sẽ`**, qui restent en tier 2. Ils occupent le même emplacement
  dans la phrase que `đã` et leurs gloses le disent, donc les monter ensemble se
  défendait. Décision de Meo : plus tard.
- **le réordonnancement du cours d'après les tiers**, qui est le changement que
  cette validation débloque et qu'elle ne fait pas.

## Tâches

- [x] Vérifier que rien ne référence la règle SVO
- [x] Supprimer l'item du contenu
- [x] `đã` et « les verbes ne changent jamais » en tier 1
- [x] Vérifier l'enchaînement réel sur la simulation
- [x] Mettre `STYLE.md` d'accord avec les items, et noter la validation
- [x] `python smoke_test.py`

## Résultat

**Terminé le :** 2026-08-15. Tiers : **8 / 10 / 9**, 27 traits `discrete` sur 34.

**Ce que ça débloque :** le classement est désormais validé, donc réordonner le
cours d'après lui devient possible. C'est là qu'il prendra son sens — aujourd'hui
le champ `tier` ne pilote rien, et l'ordre du cours reste décidé par l'ordre des
fichiers, l'espacement, et `after`.

**Une confusion levée en chemin, et elle valait la peine.** Meo pensait que
« tier 1 » voulait dire « enseigné en premier ». C'est ce que ça devrait vouloir
dire, et ça ne le veut pas encore : le classement existe et ne pilote rien. Le
malentendu était le bon instinct sur une donnée inerte.

**Un souvenir qui ne s'est pas confirmé.** Meo se rappelait avoir lié l'ordre des
mots au passé, « ensemble ». La fouille des transcrits ne trouve pas ce lien —
elle trouve celui entre « les verbes ne changent jamais » et `đã`, formulé le
matin même : *« une règle de soulagement crée une question ; la question doit
être répondue dans la foulée »*. La confusion tient probablement à ce que la
règle sur les verbes **parle des verbes**, donc ressemble à une règle d'ordre.
Le lien voulu existait, avec une autre partenaire — et il est maintenant dans le
classement autant que dans la séquence.
