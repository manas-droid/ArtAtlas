"""Utilities for loading curated essays into the database."""

from .movements.dutch_golden_age import (
    get_dutch_history_data,
    get_genre_data,
    get_technique_data,
    get_technique_data_2,
    get_materials_data,
)
from .essay_db_service import save_essay_response_to_db

from .movements.baroque import get_movement_essays

from .movements.impressionism import get_impressionism_essays


def get_dutch_golden_era_essays_and_save_to_db() -> None:
    dutch_history_response = get_dutch_history_data()
    save_essay_response_to_db(dutch_history_response)

    genre_data_response = get_genre_data()
    save_essay_response_to_db(genre_data_response)

    technique_data_response = get_technique_data()
    save_essay_response_to_db(technique_data_response)

    technique_data_2_response = get_technique_data_2()
    save_essay_response_to_db(technique_data_2_response)

    materials_data_response = get_materials_data()
    save_essay_response_to_db(materials_data_response)

def get_baroque_essays_and_save_to_db() ->None :
    baroque_essay_responses = get_movement_essays()
    for baroque_essay_res in baroque_essay_responses:
        save_essay_response_to_db(baroque_essay_res)


def get_impressionism_essay_and_save_to_db()->None:
    impressionism_essay_responses = get_impressionism_essays()
    for impressionism_essay_response in impressionism_essay_responses:
        save_essay_response_to_db(impressionism_essay_response)


def main() -> None:
    """CLI entry point to ingest all curated essays."""
    get_dutch_golden_era_essays_and_save_to_db()
    get_baroque_essays_and_save_to_db()
    get_impressionism_essay_and_save_to_db()


if __name__ == "__main__":
    main()





"""
Movements
    “Dutch Golden Age Painting”

    “Baroque Art and Drama”

    “Impressionism and Light”

    “Northern Renaissance Art”

    “Romanticism in European Painting”

Techniques / Themes

    “Chiaroscuro in Baroque Painting”

    “Portraiture in Dutch Art”

    “Maritime Painting Traditions”

    “Religious Symbolism in 17th Century Art”

This alone will massively improve:

semantic recall

conceptual explanations

demo quality


important links:

https://boisestate.pressbooks.pub/arthistory/chapter/the-golden-age-of-dutch-painting/


"""
