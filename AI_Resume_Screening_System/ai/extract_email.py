import re

def extract_email(text):

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    result = re.search(pattern, text)

    if result:

        return result.group()

    return "Not Found"