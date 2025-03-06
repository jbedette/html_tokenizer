import unicodedata

def normalize_text(text):
    text = unicodedata.normalize("NFKC", text)  # Normalize Unicode
    text = text.replace("\n", " ").strip()  # Remove unnecessary newlines
    return " ".join(text.split())  # Normalize whitespace
