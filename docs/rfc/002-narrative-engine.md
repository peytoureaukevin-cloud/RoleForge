# RFC-002 — Moteur narratif

## Objectif
Permettre au joueur d’envoyer une action et de recevoir une réponse de maître de jeu.

## Fournisseurs IA
- FakeProvider obligatoire pour jouer sans clé API.
- OpenAIProvider disponible si une clé est configurée.

## Données injectées dans le prompt
- campagne ;
- résumé ;
- héros ;
- attributs ;
- compétences ;
- traits ;
- défauts ;
- ambition ;
- inventaire ;
- historique récent ;
- action du joueur.

## Critères d’acceptation
- L’app ne plante jamais sans clé API.
- Chaque action joueur est sauvegardée.
- Chaque réponse MJ est sauvegardée.
- Le journal peut être rechargé après fermeture.
