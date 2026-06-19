from __future__ import annotations

import sqlite3


def build_prompt(
    campaign: sqlite3.Row,
    hero: sqlite3.Row,
    inventory: list[sqlite3.Row],
    skills: list[sqlite3.Row],
    history: list[sqlite3.Row],
    player_action: str,
) -> str:
    inventory_text = "\n".join(f"- {item['name']} x{item['quantity']}" for item in inventory) or "Aucun objet."
    skills_text = "\n".join(f"- {skill['skill_name']} : {skill['value']}/5" for skill in skills) or "Aucune compétence spécialisée."
    history_text = "\n".join(f"{row['role']}: {row['content']}" for row in history) or "Aucun événement récent."

    return f"""
Tu es le maître de jeu d'une aventure de jeu de rôle.

Règles :
- Réponds en français.
- Ne décide jamais à la place du joueur.
- Décris les conséquences immédiates.
- Termine par 2 à 4 pistes d'action possibles.
- Reste cohérent avec la fiche du héros, l'inventaire et le journal.
- Ne mentionne jamais que tu es une IA.
- Écris avec une atmosphère immersive, mais sans longueur excessive.

Campagne :
{campaign['name']}

Univers :
{campaign['setting']}

Résumé :
{campaign['summary'] or 'La campagne commence.'}

Héros :
{hero['name']}
Origine : {hero['origin']}
Classe : {hero['class_name']}
Portrait : {hero['portrait_description']}
Traits : {hero['traits']}
Défauts : {hero['flaws']}
Désir profond : {hero['goal'] if 'goal' in hero.keys() else ''}

Attributs :
Force {hero['strength']}
Dextérité {hero['dexterity']}
Intelligence {hero['intelligence']}
Charisme {hero['charisma']}
Constitution {hero['constitution']}

PV :
{hero['hp_current']}/{hero['hp_max']}

Compétences :
{skills_text}

Inventaire :
{inventory_text}

Historique récent :
{history_text}

Action du joueur :
{player_action}

Réponds comme un maître de jeu.
""".strip()
