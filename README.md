# RoleForge

RoleForge est une application desktop de jeu de rôle narratif solo avec Atelier du héros, Salle d’aventure, journal persistant et moteur IA branchable.

## Statut

🚧 Prototype V3 — RPG Workshop

## Lancer sur macOS

```bash
cd RoleForge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Ou :

```bash
./scripts/run_mac.sh
```

## Initialiser le dépôt Git

```bash
./scripts/init_git.sh
```

## Structure

```text
app/        Code applicatif
assets/     Ressources visuelles futures
data/       Base locale SQLite
design/     Maquettes et UI kit futurs
docs/       Vision, RFC, ADR, roadmap
scripts/    Scripts de lancement et d’initialisation
tests/      Tests futurs
```

## Prochain sprint

Sprint 1 : améliorer l’Atelier du héros avec des composants plus visuels : cartes, HeroCard, barres d’attributs et premiers talents.
