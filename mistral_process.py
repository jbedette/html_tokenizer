import os
import json
import time
import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm
from llama_cpp import Llama  # ✅ Local AI Model (No API)

# Load the Mistral model
# wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct.Q6_K.gguf -O mistral-7b.gguf

MODEL_PATH = "mistral-7b-instruct.Q6_K_M.gguf"

# MODEL_PATH = "mistral-7b.gguf"
llm = Llama(
        model_path=MODEL_PATH, 
        n_ctx=4096,
        n_threads=8,
        n_gpu_layers=0
    )  # ✅ Fully local, uses GPU if available

# Base directory where your SEC filings are stored
BASE_DIR = "sec-edgar-filings"
OUTPUT_DIR = "mistral_process"  # ✅ Changed from 'gpt_process' to 'mistral_process'

CHUNK_SIZE = 4000
BATCH_SIZE = 3
MAX_RETRIES = 3
MAX_THREADS = 3

def delete_existing_files():
    """Deletes all existing files in mistral_process before starting."""
    if os.path.exists(OUTPUT_DIR):
        for file in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(OUTPUT_DIR)
    print("🗑️ Deleted all previous files in mistral_process.\n")

def find_filing_files(base_dir):
    """Find all full-submission.txt files and extract metadata."""
    filing_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "full-submission.txt":
                parts = root.split(os.sep)
                if len(parts) >= 4 and parts[-4] == "sec-edgar-filings":
                    ticker, filing_id = parts[-3], parts[-1]
                    filing_files.append((ticker, filing_id, os.path.join(root, file)))
    return filing_files

def detect_html(content):
    """Check if a file contains HTML tags."""
    return "<html" in content.lower() or "<body" in content.lower()

def extract_text_from_html(content):
    """Extract meaningful text from HTML content."""
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def read_file_in_chunks(file_path, chunk_size=CHUNK_SIZE):
    """Generator that reads a file in chunks and processes HTML if needed."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()
    
    if detect_html(content):
        content = extract_text_from_html(content)
    
    for i in range(0, len(content), chunk_size):
        yield content[i:i + chunk_size]

def process_batch(batch):
    """Send a batch of text chunks to Mistral 7B for processing."""
    for _ in range(MAX_RETRIES):
        try:
            time.sleep(1)  # ✅ Prevent overload

            prompt = "\n\n".join(batch) + "\n\nExtract relevant sections and structure into JSON."
            response = llm(prompt, max_tokens=500)  # ✅ Process with Mistral

            return response["choices"][0]["text"].strip()

        except Exception as e:
            print(f"⚠️ LLM Error: {e}")

    print("❌ Max retries reached. Skipping batch.")
    return ""

def load_existing_content(output_filename):
    """Loads existing content from a JSON file if it exists."""
    if os.path.exists(output_filename):
        with open(output_filename, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data.get("full_text", "")
            except json.JSONDecodeError:
                print(f"⚠️ Warning: {output_filename} is corrupted. Creating a new file.")
                return ""
    return ""

def process_single_filing(ticker, filing_id, file_path, progress_bar):
    """Processes a single SEC filing using Mistral 7B."""
    progress_bar.set_description(f"Processing {ticker}-{filing_id}")
    output_filename = os.path.join(OUTPUT_DIR, f"{ticker}_{filing_id}.json")

    existing_content = load_existing_content(output_filename)
    combined_text = existing_content

    batch = []
    chunks = list(read_file_in_chunks(file_path))

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for i, chunk in enumerate(tqdm(chunks, desc=f"Processing {ticker}-{filing_id}", leave=False)):
            batch.append(chunk)
            if len(batch) >= BATCH_SIZE:
                futures.append(executor.submit(process_batch, batch[:]))
                batch = []

        if batch:
            futures.append(executor.submit(process_batch, batch))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                combined_text += result + "\n\n"

    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump({"ticker": ticker, "filing_id": filing_id, "full_text": combined_text}, output_file, indent=4)

    progress_bar.update(1)
    print(f"✅ Saved {output_filename} (Appended)")

def process_filings():
    """Process all filings using Mistral 7B locally."""
    delete_existing_files()
    filings = find_filing_files(BASE_DIR)

    print(f"🔄 Processing {len(filings)} filings...\n")

    with tqdm(total=len(filings), desc="Overall Progress") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(process_single_filing, ticker, filing_id, file_path, progress_bar): (ticker, filing_id) for ticker, filing_id, file_path in filings}

            for future in concurrent.futures.as_completed(futures):
                ticker, filing_id = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Error processing {ticker} {filing_id}: {e}")

    print("\n✅ All filings processed!")

# Run the optimized processing function
process_filings()
