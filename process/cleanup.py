import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def remove_stopwords(text):
    words = text.split()
    return " ".join([word for word in words if word.lower() not in stop_words])
