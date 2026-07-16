import re

def extract_phone(text):

    pattern = r"\b\d{10}\b"

    result = re.search(pattern, text)

    if result:

        return result.group()

    return "Not Found"