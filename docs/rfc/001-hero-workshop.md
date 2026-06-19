# RFC-001 — Atelier du héros

## Objectif
Transformer la création de personnage en véritable expérience RPG.

## V1 attendue
L’utilisateur doit pouvoir créer un héros avec :
- nom ;
- origine ;
- classe ;
- attributs ;
- compétences ;
- traits ;
- défauts ;
- ambition ;
- inventaire de départ.

## Règles
- Attributs de base : 8.
- Maximum : 18.
- Points d’attributs disponibles : 20.
- Points de compétences disponibles : 12.
- Impossible de valider sans nom.
- Impossible de valider si les points ne sont pas correctement dépensés.

## Critères d’acceptation
- La création est guidée.
- Les points restants sont toujours visibles.
- La fiche finale est sauvegardée en SQLite.
- Le héros est visible dans la Salle d’aventure.
