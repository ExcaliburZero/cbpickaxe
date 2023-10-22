"""
Scripts for data mining the game Cassette Beasts.
"""
from .extract_translation import main_without_args as extract_translation_main
from .get_move_users import main_without_args as get_move_users_main
from .generate_docs import main_without_args as generate_docs_main
from .generate_monster_animations import (
    main_without_args as generate_monster_animations_main,
)

__all__ = [
    "extract_translation_main",
    "get_move_users_main",
    "generate_docs_main",
    "generate_monster_animations_main",
]
