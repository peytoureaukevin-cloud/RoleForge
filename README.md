# RoleForge

RoleForge est un prototype d'application desktop pour créer un héros de jeu de rôle, lancer une aventure solo et connecter un moteur narratif IA.

## État du projet

🚧 Développement initial — base technique en cours de stabilisation.

## Lancer sur Mac

```bash
bash scripts/run_mac.sh
```

Le script crée l'environnement virtuel si nécessaire, installe les dépendances, puis lance l'application.

## Tester

```bash
python -m pytest
```

## Structure

```text
app/
  ai/          Fournisseurs IA
  core/        Règles métier, dés, prompt, moteur de jeu
  database/    SQLite et accès aux données
  ui/          Interface PySide6
docs/
  rfc/         Spécifications courtes par fonctionnalité
scripts/       Scripts de lancement et d'initialisation Git
tests/         Tests automatisés
```

## Sprint actuel

**Sprint 0 — stabilisation du repo**

- centraliser les règles de création du héros ;
- ajouter des tests simples ;
- clarifier le lancement ;
- éviter les grosses fonctionnalités avant une base stable.

## Prochaine cible

**Sprint 1 — Atelier du héros premium**

- cartes de classe plus visuelles ;
- composant HeroCard ;
- affichage plus RPG des attributs ;
- première version d'arbre de talents.


## Sprint 2

La Salle d'aventure a été retravaillée pour ne plus ressembler à un chat brut : journal visuel, intentions rapides, onglets Héros/Sac/Journal et HeroCard réutilisée en partie.


## Sprint 3 — Inventaire verrouillé & Codex

RoleForge applique maintenant une règle de design importante : le joueur consulte son inventaire, mais ne l'édite pas librement pendant l'aventure.

Les objets et les découvertes sont ajoutés par le Conteur via des effets structurés, puis sauvegardés dans l'inventaire, le Codex et le journal.
