import os
import platform
import re
import spacy
import nltk
from tqdm import tqdm
from nltk.tokenize import sent_tokenize
# from concurrent.futures import ProcessPoolExecutor
nltk.download('punkt')
nltk.download('punkt_tab')

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# Define Parent Input and Output Folder Paths
PARENT_INPUT_FOLDER = "sec-edgar-filings"
PARENT_OUTPUT_FOLDER = "cleaned_10k_reports"

# Cleans 10-K text by removing unwanted characters, metadata, and formatting noise.
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'<.*?>', ' ', text)  # Remove HTML/SGML tags
    text = re.sub(r'[^a-zA-Z0-9.,;?!\s]', '', text) # Remove special characters EXCEPT basic punctuation
    text = re.sub(r'begin privacyenhanced message.*?dkhtm', '', text, flags=re.DOTALL)  # Remove SEC metadata blocks
    text = re.sub(r'(accession number|standard industrial classification|file number).*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[\n]+', '\n', text)  # Normalize line breaks
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip()

# Splits text into sections based on common 10-K headers.
def chunk_text(text):
    headers = [
        "business", "risk factors", "management’s discussion and analysis",
        "financial statements", "legal proceedings", "quantitative and qualitative disclosures"
    ]
    
    pattern = re.compile(r'^\s*(' + '|'.join(headers) + r')\s*$', re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(text))

    sections = {}
    prev_idx = 0
    prev_header = "introduction"

    for match in matches:
        section_title = match.group(1).strip().lower()
        sections[prev_header] = text[prev_idx:match.start()].strip()
        prev_idx = match.end()
        prev_header = section_title

    sections[prev_header] = text[prev_idx:].strip()  # Last section
    return sections



def account_for_system(relative_path):
    if platform.system() == "Windows":
        rel = relative_path.split("\\",2)
        return rel[0] + "_" + rel[2] +".txt"
    else:
        rel = relative_path.split("/",2)
        return rel[0] + "_" + rel[2] +".txt"


# Walk through all subdirectories in input folder
if __name__ == "__main__":
    # Ensure output folder exists
    os.makedirs(PARENT_OUTPUT_FOLDER, exist_ok=True)

    # Remove old processed files before starting
    if os.path.exists(PARENT_OUTPUT_FOLDER):
        print("🗑️ Deleting old processed files...")
        for root, dirs, files in os.walk(PARENT_OUTPUT_FOLDER, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

    # write
    for root, _, files in os.walk(PARENT_INPUT_FOLDER):
        for filename in tqdm(files):
            if filename.endswith(".txt"):
                input_path = os.path.join(root, filename)

                # 1: Construct relative path for output
                relative_path = os.path.relpath(root, PARENT_INPUT_FOLDER)
                write_name = account_for_system(relative_path)

                output_path = os.path.join(PARENT_OUTPUT_FOLDER, write_name)

                with open(input_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # 2: Clean the text
                text = clean_text(text)

                # 3: Split into sections
                sections = chunk_text(text)

                # 4: Tokenize sentences
                for section, content in sections.items():
                    sections[section] = " ".join(sent_tokenize(content))

                # 5: Save to output file
                with open(output_path, "w", encoding="utf-8") as f:
                    for section, content in sections.items():
                        f.write(f"\n\n### {section.upper()} ###\n{content}\n")

    print(f"✅ Processing complete! Cleaned files saved in {PARENT_OUTPUT_FOLDER}")
