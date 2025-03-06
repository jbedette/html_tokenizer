#! /bin/bash
pip install spacy nltk tqdm
python -m spacy download en_core_web_sm python-magic beautifulsoup4 pandas lxml
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('punkt_tab')"