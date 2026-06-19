# RFC-005 — Salle d'aventure lisible

## Objectif

La Salle d'aventure ne doit pas ressembler à un simple chat. Elle doit donner l'impression d'ouvrir une table de jeu : narration centrale, intentions rapides, fiche de héros visible, inventaire et traces persistantes.

## Décisions V1

- Remplacer l'affichage brut du journal par des entrées visuelles : Vous, Conteur, Système.
- Ajouter des intentions rapides : Observer, Écouter, Parler, Discrétion, Inventaire, Intuition.
- Remplacer le panneau texte unique par trois onglets : Héros, Sac, Journal.
- Réutiliser `HeroCard` dans l'aventure afin que le héros reste le centre du produit.
- Conserver chaque jet de D20 comme entrée système.

## Critères d'acceptation

- Une campagne sans entrée affiche une page blanche accueillante.
- Chaque action apparaît dans le journal avec un style distinct.
- Le joueur peut remplir rapidement le champ d'action grâce aux intentions rapides.
- La fiche héros, l'inventaire et le journal restent consultables sans quitter l'aventure.
- Le D20 affiche le dernier résultat et le sauvegarde.

## Hors scope

- Combat tactique.
- Cartes.
- Images de lieux.
- Gestion avancée des quêtes.
