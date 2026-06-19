# RFC-004 — HeroCard et Atelier du héros en cartes

## Statut

Validée pour Sprint 1.

## Objectif

Transformer l'Atelier du héros en expérience RPG visuelle, moins proche d'un formulaire classique.

## Décisions

- Introduire un composant réutilisable `HeroCard`.
- Introduire des cartes de choix pour univers, origine et vocation.
- Remplacer les lignes de points trop techniques par des allocateurs visuels avec barres.
- Garder les règles V1 : 20 points d'attributs, 12 points de compétences, création impossible si les points ne sont pas exactement répartis.
- Garder PySide6 et SQLite.

## Composants créés

### `ChoiceCard`

Carte cliquable réutilisable pour les choix importants.

Utilisations immédiates :

- ton de campagne ;
- origine ;
- vocation.

Utilisations futures :

- talents ;
- objets ;
- compagnons ;
- lieux ;
- codex.

### `PointAllocator`

Composant d'attribution de points avec boutons `−` / `+` et barre visuelle.

### `HeroCard`

Résumé vivant du héros en cours de création.

Doit être réutilisé plus tard dans :

- Salle d'aventure ;
- Musée ;
- Bibliothèque ;
- Marketplace.

## Critères d'acceptation

- L'utilisateur peut créer une campagne et un héros.
- Les choix majeurs se font avec des cartes.
- Le aperçu `HeroCard` se met à jour pendant la création.
- Les presets de vocation remplissent attributs, compétences et inventaire.
- Les tests existants passent.
