from __future__ import annotations

ATTRIBUTE_MIN = 8
ATTRIBUTE_MAX = 18
ATTRIBUTE_POINTS = 20
SKILL_MIN = 0
SKILL_MAX = 5
SKILL_POINTS = 12

ATTRIBUTES = [
    ("strength", "Force", "Puissance physique, intimidation, armes lourdes."),
    ("dexterity", "Dextérité", "Adresse, discrétion, réflexes."),
    ("intelligence", "Intelligence", "Analyse, savoirs, stratégie."),
    ("charisma", "Charisme", "Présence, persuasion, mensonge, commandement."),
    ("constitution", "Constitution", "Endurance, résistance, points de vie."),
]

# Compatibility helper: some UI code expects 3-tuples.
def attribute_rows() -> list[tuple[str, str, str]]:
    return [(row[0], row[1], row[-1]) for row in ATTRIBUTES]

SKILLS = [
    ("combat", "Combat"),
    ("survival", "Survie"),
    ("stealth", "Furtivité"),
    ("speech", "Discours"),
    ("arcana", "Arcanes / Tech"),
    ("craft", "Artisanat"),
]

GOALS = [
    "Protéger quelqu'un",
    "Retrouver une vérité",
    "Devenir puissant",
    "Réparer une faute",
]

CLASS_PRESETS = {
    "Guerrier": {
        "attrs": {"strength": 16, "dexterity": 12, "intelligence": 10, "charisma": 10, "constitution": 15},
        "skills": {"combat": 5, "survival": 2, "stealth": 0, "speech": 1, "arcana": 0, "craft": 4},
        "inventory": "épée usée\nbouclier marqué\nrations de voyage",
        "pitch": "Encaisser, frapper, tenir la ligne.",
    },
    "Rôdeur": {
        "attrs": {"strength": 12, "dexterity": 16, "intelligence": 11, "charisma": 10, "constitution": 14},
        "skills": {"combat": 3, "survival": 5, "stealth": 3, "speech": 0, "arcana": 0, "craft": 1},
        "inventory": "arc court\ncouteau de chasse\ncarte incomplète",
        "pitch": "Observer, survivre, frapper juste.",
    },
    "Mage": {
        "attrs": {"strength": 8, "dexterity": 12, "intelligence": 18, "charisma": 12, "constitution": 13},
        "skills": {"combat": 0, "survival": 1, "stealth": 0, "speech": 2, "arcana": 5, "craft": 4},
        "inventory": "carnet d'études\nbâton gravé\nfiole d'encre noire",
        "pitch": "Comprendre, manipuler, révéler.",
    },
    "Voleur": {
        "attrs": {"strength": 9, "dexterity": 18, "intelligence": 12, "charisma": 12, "constitution": 12},
        "skills": {"combat": 2, "survival": 0, "stealth": 5, "speech": 2, "arcana": 0, "craft": 3},
        "inventory": "dague fine\ncrochets rouillés\ncapuche sombre",
        "pitch": "Entrer, prendre, disparaître.",
    },
    "Diplomate": {
        "attrs": {"strength": 8, "dexterity": 10, "intelligence": 15, "charisma": 18, "constitution": 12},
        "skills": {"combat": 0, "survival": 0, "stealth": 1, "speech": 5, "arcana": 2, "craft": 4},
        "inventory": "sceau brisé\nlettre non envoyée\nvêtements impeccables",
        "pitch": "Convaincre, négocier, survivre par la parole.",
    },
    "Contrebandier": {
        "attrs": {"strength": 10, "dexterity": 16, "intelligence": 12, "charisma": 14, "constitution": 11},
        "skills": {"combat": 2, "survival": 1, "stealth": 3, "speech": 3, "arcana": 1, "craft": 2},
        "inventory": "blaster fatigué\nveste élimée\n83 crédits",
        "pitch": "Improviser, mentir, disparaître.",
    },
}


def spent(values: list[int], minimum: int) -> int:
    return sum(value - minimum for value in values)


def remaining(values: list[int], minimum: int, pool: int) -> int:
    return pool - spent(values, minimum)


def validate_exact_pool(values: list[int], minimum: int, maximum: int, pool: int) -> tuple[bool, str]:
    if any(value < minimum or value > maximum for value in values):
        return False, f"Chaque valeur doit être comprise entre {minimum} et {maximum}."
    points_left = remaining(values, minimum, pool)
    if points_left != 0:
        return False, f"Il reste {points_left} point(s) à répartir." if points_left > 0 else f"Il y a {-points_left} point(s) en trop."
    return True, ""
