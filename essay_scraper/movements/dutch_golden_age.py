import requests
from bs4 import BeautifulSoup

from essay_scraper.movements.common import divide_into_managable_chunks
from essay_scraper.essay_model import EssayCategory, EssayResponse


# Explains what the dutch golden age was about
def get_dutch_history_data()->EssayResponse:
    source_url = 'https://rauantiques.com/blogs/canvases-carats-and-curiosities/dutch-golden-age-dawn-new-art-market'

    response = requests.get(source_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    paragraphs = soup.select('.rte p')

    history_paras = paragraphs[0:3]
    chunks = []

    divide_into_managable_chunks(history_paras[0], chunks)
    divide_into_managable_chunks(history_paras[2], chunks)

    return {'chunks':chunks , 'essay_type': EssayCategory.MOVEMENT,  'essay_title': 'Dutch Golden Age Dawn New Art Market', 'source': 'Rauantiques' , 'source_url': source_url}





"""
Get Information about the styles popularized in the 16th - 17th Century, Can be common for other movements as well
"""
def get_technique_data()->EssayResponse:
    source_url = 'http://theartstory.org/definition/chiaroscuro-tenebrism-sfumato/'
    response = requests.get(source_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    summary_para = soup.find(class_='article-text summary-text')
    chunks = []

    divide_into_managable_chunks(summary_para, chunks)

        

    key_artworks = soup.find_all(class_="artwork-description")

    for key_artwork in key_artworks[0:6]:
        divide_into_managable_chunks(key_artwork, chunks)

    technique_information_paras = soup.find_all(class_='article-text')

    for technique_information  in technique_information_paras[-10:-5]:
        divide_into_managable_chunks(technique_information, chunks)

    return {'chunks':chunks, 'essay_type': EssayCategory.TECHNIQUE, 'essay_title': 'Chiaroscuro, Tenebrism and Sfumato', 'source': 'The Art Story', 'source_url':  source_url}



"""
Has details about brushwork and technical details about the dutch artist' approach towards painting
"""
def get_technique_data_2()->EssayResponse:
    source_url = 'https://fiveable.me/art-in-the-dutch-golden-age/unit-13'

    response = requests.get(source_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    listOfDetails = soup.find_all(class_='MuiBox-root mui-19idom')

    chunks = []

    divide_into_managable_chunks(listOfDetails[4], chunks)

    return {'chunks': chunks, 'essay_type': EssayCategory.TECHNIQUE, 'essay_title':'Art in the Dutch Golden Age - Unit 13', 'source':'Fiveable.me', 'source_url': source_url}
    
"""
Describes what materials were used
"""
def get_materials_data()->EssayResponse:
    source_url = 'https://fiveable.me/art-in-the-dutch-golden-age/unit-7'

    response = requests.get(source_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    listOfDetails = soup.find_all(class_='MuiBox-root mui-19idom')
    chunks = []

    divide_into_managable_chunks(listOfDetails[7], chunks)
    divide_into_managable_chunks(listOfDetails[8], chunks)
    divide_into_managable_chunks(listOfDetails[10], chunks)

    return {'chunks': chunks, 'essay_type': EssayCategory.TECHNIQUE, 'essay_title':'Art in the Dutch Golden Age - Unit 7', 'source':'Fiveable.me', 'source_url': source_url}




def get_genre_data()->EssayResponse:
    source_url = 'https://www.theartstory.org/movement/dutch-golden-age/'

    response = requests.get(source_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all(class_='article-text')

    chunks = []
    for i in [13,14,15,16,17,19,20,27]:
        divide_into_managable_chunks(articles[i], chunks)


    return {'chunks': chunks, 'essay_title': 'Dutch Golden Age', 'essay_type': EssayCategory.GENRE, 'source': 'The Art Story', 'source_url':source_url}

