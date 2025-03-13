import os
import json
import time
from openai import OpenAI
from bs4 import BeautifulSoup

client = OpenAI(api_key("")

# Base directory where your SEC filings are stored
BASE_DIR = "sec-edgar-filings"

# Directory to save processed JSON files
OUTPUT_DIR = "gpt_process"

# OpenAI API parameters
MODEL = "gpt-4-turbo"
CHUNK_SIZE = 4000
MAX_RETRIES = 3  # Retries on API failure

def find_filing_files(base_dir):
    """Find all full-submission.txt files and extract metadata."""
    filing_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "full-submission.txt":
                parts = root.split(os.sep)

                # Ensure we are capturing {ticker} and {ID}, not "10-K"
                if len(parts) >= 4 and parts[-4] == "sec-edgar-filings":
                    ticker, filing_id = parts[-3], parts[-1]  # Correct extraction
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

def process_chunk(chunk):
    """Send a chunk to OpenAI and return the raw response."""
    for _ in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Extract relevant sections and format them into a structured JSON object."},
                    {"role": "user", "content": chunk}
                ]
            )
            response_text = response.choices[0].message.content.strip()
            if not response_text:
                raise ValueError("Empty response from OpenAI API")
            
            return response_text  # Return raw text instead of JSON

        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")

        time.sleep(2)  # Wait before retrying

    print("❌ Max retries reached. Skipping this chunk.")
    return ""

def process_filings():
    """Process all filings and save combined raw responses per file."""
    filings = find_filing_files(BASE_DIR)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for ticker, filing_id, file_path in filings:
        print(f"Processing {ticker} - {filing_id}")

        combined_text = ""  # Store all raw responses

        for chunk in read_file_in_chunks(file_path):
            raw_response = process_chunk(chunk)
            if raw_response:
                combined_text += raw_response + "\n\n"  # Separate chunks with double newline

        # Save final combined response as JSON
        output_filename = os.path.join(OUTPUT_DIR, f"{ticker}_{filing_id}.json")
        with open(output_filename, "w", encoding="utf-8") as output_file:
            json.dump({"ticker": ticker, "filing_id": filing_id, "full_text": combined_text}, output_file, indent=4)

        print(f"✅ Saved {output_filename}")

    print("✅ Processing complete.")

# Run the processing function
process_filings()
