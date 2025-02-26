# html_tokenizer

So I'm making a NLP AI to summarize 10-k reports. I've got my data, but my data cleaning isn't up to snuff, and things have begun spiraling out of control. My target data is using some inline html/css styling that I'm having a hard time dealing with. The patterns switch very often throughout the files and they are larger files than I want to deal with manually. 

I'm splitting out the tokenization into it's own little project that I will then re-integrate with the larger ML pipeline. 

# setup
Currently the required packages need python 3.11, so create a python 3.11 venv

1. set up virtual environment

`python -m venv venv`

2. turn on venv

`venv\Scripts\activate`


4. install necessary packages


`pip install spacy nltk tqdm`

5. get the other things the packages need
`python -m spacy download en_core_web_sm`
`python -c "import nltk; nltk.download('punkt')"`
`python -c "import nltk; nltk.download('punkt_tab')"`

