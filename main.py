# Final Pipeline Overview

#     Detect format (detect_format())
#     Extract & clean:
#         HTML → clean_html()
#         Plaintext → normalize_text()
#     Extract sections (extract_sections())
#     Extract tables (extract_tables())
#     Post-process:
#         Remove stopwords
#         Apply lemmatization (optional)
import os
import threading
from pathlib import Path
from process import detect, html_parse, nlp_extract, handle_tables, conv_plaintext, cleanup

# Define input/output directories
INPUT_DIR = "sec-edgar-filings"
OUTPUT_DIR = "cleaned_10k_reports"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Process a single report file
def process_report(file_path, ticker, filing_id):
    try:
        # Step 1: Read file contents
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Name and set output for the processed report as {ticker}_{ID}.txt
        output_filename = f"{ticker}_{filing_id}.txt"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Step 2: Detect format (HTML or plaintext)
        file_type = detect.detect_format(file_path)

        # Step 3: Process based on type
        if file_type == "html":
            processed_text = html_parse.clean_html(raw_content)
        else:
            processed_text = conv_plaintext.normalize_text(raw_content)

        # Step 4: Extract meaningful sections (e.g., Risk Factors, MD&A)
        sections = nlp_extract.extract_sections(processed_text,output_filename)

        # Step 5: Extract financial tables (if HTML)
        if file_type == "html":
            tables = handle_tables.extract_tables(raw_content)

        # Step 6: Cleanup and final text processing
        cleaned_text = cleanup.remove_stopwords(processed_text)


        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"✔ Processed {output_filename}")

    except Exception as e:
        print(f"❌ Error processing {ticker}/{filing_id}: {e}")

# # Multi-threaded processing function
# def process_all_reports():
#     threads = []

#     # Traverse the EDGAR filings directory
#     for ticker in os.listdir(INPUT_DIR):
#         ticker_path = os.path.join(INPUT_DIR, ticker)

#         if os.path.isdir(ticker_path):
#             for filing_id in os.listdir(ticker_path):
#                 filing_path = os.path.join(ticker_path, filing_id, "full-submission.txt")

#                 if os.path.exists(filing_path):
#                     thread = threading.Thread(target=process_report, args=(filing_path, ticker, filing_id))
#                     threads.append(thread)
#                     thread.start()

#                     # Limit concurrent threads to avoid resource exhaustion
#                     if len(threads) >= 10:  # Adjust based on system performance
#                         for t in threads:
#                             t.join()
#                         threads = []

#     # Ensure all threads complete
#     for t in threads:
#         t.join()

#     print("✅ All reports processed!")

# def process_all_reports():
#     threads = []

#     print(f"Scanning directory: {INPUT_DIR}")
#     if not os.path.exists(INPUT_DIR):
#         print(f"❌ ERROR: Input directory {INPUT_DIR} does not exist.")
#         return

#     for ticker in os.listdir(INPUT_DIR):
#         ticker_path = os.path.join(INPUT_DIR, ticker)
#         print(f"Checking ticker folder: {ticker_path}")

#         if os.path.isdir(ticker_path):
#             for filing_id in os.listdir(ticker_path):
#                 filing_path = os.path.join(ticker_path, filing_id, "full-submission.txt")
#                 print(f"Looking for: {filing_path}")

#                 if os.path.exists(filing_path):
#                     print(f"✅ Found: {filing_path}")
#                     thread = threading.Thread(target=process_report, args=(filing_path, ticker, filing_id))
#                     threads.append(thread)
#                     thread.start()

#                     # Limit concurrent threads to avoid resource exhaustion
#                     if len(threads) >= 10:
#                         for t in threads:
#                             t.join()
#                         threads = []

#     for t in threads:
#         t.join()

#     print("✅ All reports processed!")

def process_all_reports():
    threads = []
    count = 0
    print(f"Scanning directory: {INPUT_DIR}")
    if not os.path.exists(INPUT_DIR):
        print(f"❌ ERROR: Input directory {INPUT_DIR} does not exist.")
        return

    for ticker in os.listdir(INPUT_DIR):
        ticker_path = os.path.join(INPUT_DIR, ticker, "10-K")  # Updated path
        print(f"Checking ticker folder: {ticker_path}")

        if os.path.isdir(ticker_path):
            for filing_id in os.listdir(ticker_path):
                filing_path = os.path.join(ticker_path, filing_id, "full-submission.txt")  # Corrected path

                if os.path.exists(filing_path):
                    count += 1
                    print(f"=> {count}, {filing_path}")
                    thread = threading.Thread(target=process_report, args=(filing_path, ticker, filing_id))
                    threads.append(thread)
                    thread.start()

                    # Limit concurrent threads to avoid resource exhaustion
                    if len(threads) >= 10:
                        for t in threads:
                            t.join()
                        threads = []

    for t in threads:
        t.join()

    print("✅ All reports processed!")


# Run the pipeline
if __name__ == "__main__":
    process_all_reports()
