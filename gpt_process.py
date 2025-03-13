import os
import json
import openai
import time
import concurrent.futures
from bs4 import BeautifulSoup
from threading import Semaphore
from tqdm import tqdm  # ✅ Progress bar
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

# Base directory where your SEC filings are stored
BASE_DIR = "sec-edgar-filings"

# Directory to save processed JSON files
OUTPUT_DIR = "gpt_process"

# OpenAI API parameters
MODEL = "gpt-3.5-turbo"  # ✅ Cheaper model
CHUNK_SIZE = 4000
BATCH_SIZE = 3  # ✅ Group chunks into batches for fewer API calls
MAX_RETRIES = 3  # ✅ Retries on API failure
MAX_THREADS = 3  # ✅ Controls parallel processing
API_SEMAPHORE = Semaphore(2)  # ✅ Prevents excessive API calls

def delete_existing_files():
    """Deletes all existing files in gpt_process before starting."""
    if os.path.exists(OUTPUT_DIR):
        for file in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(OUTPUT_DIR)  # ✅ Ensure directory exists
    print("🗑️ Deleted all previous files in gpt_process.\n")

def find_filing_files(base_dir):
    """Find all full-submission.txt files and extract metadata."""
    filing_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "full-submission.txt":
                parts = root.split(os.sep)
                if len(parts) >= 4 and parts[-4] == "sec-edgar-filings":
                    ticker, filing_id = parts[-3], parts[-1]  # ✅ Correct `filing_id`
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
    """Send a batch of text chunks to OpenAI for processing with rate limiting."""
    for attempt in range(MAX_RETRIES):
        try:
            with API_SEMAPHORE:  # ✅ Limit concurrent API calls
                time.sleep(2)  # ✅ Prevent hitting rate limits

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "system", "content": "Extract relevant sections and format them into structured JSON."}] +
                              [{"role": "user", "content": chunk} for chunk in batch]
                )

                response_text = "\n\n".join([choice.message.content.strip() for choice in response.choices])
                if not response_text:
                    raise ValueError("Empty response from OpenAI API")

                return response_text  # ✅ Return combined raw text

        except openai.RateLimitError:
            wait_time = (2 ** attempt) * 5  # ✅ Exponential backoff
            print(f"⚠️ Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")

    print("❌ Max retries reached. Skipping this batch.")
    return ""

def load_existing_content(output_filename):
    """Loads existing content from a JSON file if it exists."""
    if os.path.exists(output_filename):
        with open(output_filename, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data.get("full_text", "")  # ✅ Preserve previous content
            except json.JSONDecodeError:
                print(f"⚠️ Warning: {output_filename} is corrupted. Creating a new file.")
                return ""
    return ""

def process_single_filing(ticker, filing_id, file_path, progress_bar):
    """Processes a single SEC filing with rate-limited API requests and a progress bar."""
    progress_bar.set_description(f"Processing {ticker}-{filing_id}")
    output_filename = os.path.join(OUTPUT_DIR, f"{ticker}_{filing_id}.json")

    existing_content = load_existing_content(output_filename)  # ✅ Load previous data
    combined_text = existing_content  # ✅ Append to existing content

    batch = []  # ✅ Store batch chunks
    chunks = list(read_file_in_chunks(file_path))  # ✅ Get total chunks for progress tracking

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for i, chunk in enumerate(tqdm(chunks, desc=f"Processing {ticker}-{filing_id}", leave=False)):
            batch.append(chunk)
            if len(batch) >= BATCH_SIZE:
                futures.append(executor.submit(process_batch, batch[:]))
                batch = []  # ✅ Reset batch

        if batch:
            futures.append(executor.submit(process_batch, batch))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                combined_text += result + "\n\n"  # ✅ Append new content

    # ✅ Save appended results
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump({"ticker": ticker, "filing_id": filing_id, "full_text": combined_text}, output_file, indent=4)

    progress_bar.update(1)  # ✅ Update progress bar
    print(f"✅ Saved {output_filename} (Appended)")

def process_filings():
    """Process all filings with controlled concurrency and a progress bar."""
    delete_existing_files()  # ✅ Delete all files before starting
    filings = find_filing_files(BASE_DIR)

    print(f"🔄 Processing {len(filings)} filings...\n")

    with tqdm(total=len(filings), desc="Overall Progress") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(process_single_filing, ticker, filing_id, file_path, progress_bar): (ticker, filing_id) for ticker, filing_id, file_path in filings}

            for future in concurrent.futures.as_completed(futures):
                ticker, filing_id = futures[future]
                try:
                    future.result()  # ✅ Wait for completion
                except Exception as e:
                    print(f"❌ Error processing {ticker} {filing_id}: {e}")

    print("\n✅ All filings processed!")

# Run the optimized processing function
process_filings()
