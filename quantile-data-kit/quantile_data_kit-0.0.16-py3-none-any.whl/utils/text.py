def clean_text(text: str) -> str:
    """Perform basic text cleaning
    1. Normalize special characters
    2. Remove special quotes

    Args:
        text (str): The text you want to clean

    Returns:
        str: The cleaned text
    """
    text = text.replace("è", "e")
    text = text.replace("é", "e")
    text = text.replace("ê", "e")
    text = text.replace("ë", "e")
    text = text.replace("ì", "i")
    text = text.replace("í", "i")
    text = text.replace("î", "i")
    text = text.replace("ï", "i")
    text = text.replace("ò", "o")
    text = text.replace("ó", "o")
    text = text.replace("ô", "o")
    text = text.replace("õ", "o")
    text = text.replace("ö", "o")
    text = text.replace("ù", "u")
    text = text.replace("ú", "u")
    text = text.replace("û", "u")
    text = text.replace("ü", "u")
    text = text.replace("ç", "c")
    text = text.replace("‘", "")
    text = text.replace("’", "")
    text = text.replace("©", "")

    return text
