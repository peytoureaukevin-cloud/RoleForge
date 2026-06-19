# RFC-003 — Règles de création du héros

## Objectif

Centraliser les règles chiffrées de création du héros pour éviter que l'interface contienne la logique métier.

## Règles V1

- Attribut minimum : 8
- Attribut maximum : 18
- Points d'attributs à répartir : 20
- Compétence minimum : 0
- Compétence maximum : 5
- Points de compétences à répartir : 12

## Critères d'acceptation

- L'interface utilise les constantes du module `app.core.character_rules`.
- Les tests vérifient les pools de points.
- Les prochains écrans de montée de niveau réutiliseront ce module.
