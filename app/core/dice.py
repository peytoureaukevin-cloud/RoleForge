from __future__ import annotations

import random


def roll(sides: int = 20) -> int:
    if sides < 2:
        raise ValueError("Un dé doit avoir au moins deux faces.")
    return random.randint(1, sides)
