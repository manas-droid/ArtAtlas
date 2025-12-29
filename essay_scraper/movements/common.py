from bs4 import BeautifulSoup, Tag
import requests


def divide_into_managable_chunks(data:Tag, chunks):
    divide_str_into_managable_chunks(data=data.get_text().split('.'), chunks=chunks)


def divide_str_into_managable_chunks(data:list[str], chunks):
    """
    Split a list of sentence-like strings into word-bounded chunks.

    This is used before DB insertion + embedding generation, so it must:
    - avoid empty chunks
    - avoid runaway chunk sizes
    - always flush the final remainder
    """
    if not data:
        return

    max_words_per_chunk = 150

    current_parts: list[str] = []
    current_words = 0

    def flush() -> None:
        nonlocal current_parts, current_words
        text = " ".join(current_parts).strip()
        text = " ".join(text.split())  # normalize whitespace
        text = text.replace("\x00", "")  # DB safety
        if text:
            chunks.append(text)
        current_parts = []
        current_words = 0

    for raw_sentence in data:
        sentence = (raw_sentence or "").strip()
        if not sentence:
            continue

        # Ensure the sentence ends cleanly; split('.') drops punctuation.
        if not sentence.endswith((".", "!", "?")):
            sentence = sentence + "."

        words_in_sentence = len(sentence.split())

        # If a single sentence is enormous, hard-split by words.
        if words_in_sentence > max_words_per_chunk:
            flush()
            words = sentence.split()
            for start in range(0, len(words), max_words_per_chunk):
                piece = " ".join(words[start : start + max_words_per_chunk]).strip()
                if piece:
                    chunks.append(piece.replace("\x00", ""))
            continue

        if current_words + words_in_sentence > max_words_per_chunk and current_parts:
            flush()

        current_parts.append(sentence)
        current_words += words_in_sentence

        if current_words >= max_words_per_chunk:
            flush()

    flush()


def get_soup(source_url:str)->BeautifulSoup:
    response = requests.get(source_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    return soup
