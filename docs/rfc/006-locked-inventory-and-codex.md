# RFC-006 — Inventaire verrouillé et Codex V1

## Décision

Pendant l'aventure, le joueur ne modifie pas librement son inventaire.

Il peut consulter son sac, lire les descriptions et comprendre l'origine des objets, mais les ajouts et retraits sont appliqués uniquement par le Conteur.

## Motivation

Un inventaire éditable en cours de partie casse l'illusion RPG. Dans un jeu de rôle, le sac du héros évolue par l'action, la récompense, l'achat, le vol, la perte ou la décision du maître du jeu — pas par modification manuelle libre.

## Implémentation V1

Le Conteur peut ajouter un bloc technique à sa réponse :

```roleforge_effects
{"inventory_changes":[{"action":"add","name":"Fiole de soin","quantity":1,"rarity":"commun"}],"codex_discoveries":[{"kind":"objet","name":"Fiole de soin","description":"Une petite fiole rouge."}]}
```

L'application :

1. retire ce bloc de la narration visible ;
2. applique les changements d'inventaire ;
3. ajoute les découvertes au Codex ;
4. écrit une entrée système dans le journal.

## Critères d'acceptation

- Le joueur ne dispose d'aucun bouton d'ajout/suppression d'objet en aventure.
- Le sac affiche clairement qu'il est verrouillé.
- Le Conteur peut ajouter un objet.
- Le Conteur peut retirer un objet.
- Le Conteur peut créer une entrée de Codex.
- Les effets appliqués sont tracés dans le journal.
