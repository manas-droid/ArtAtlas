from .movements.dutch_golden_age import get_dutch_history_data, get_genre_data, get_technique_data, get_technique_data_2, get_materials_data
from .essay_db_service import save_essay_response_to_db




def get_essays_and_save_to_db():
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


get_essays_and_save_to_db()





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