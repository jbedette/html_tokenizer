from bs4 import BeautifulSoup
import os
import json
import re

def find_table_of_contents(html_content, name):
    """Extracts TOC from 10-K HTML filings using BeautifulSoup and logs all tables."""
    soup = BeautifulSoup(html_content, "html.parser")  # Use 'html.parser' for better parsing

    # Ensure output directory exists
    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    # Extract all tables
    tables = soup.find_all("table")

    # Locate TOC by checking <table> and <caption> text
    toc_table = None
    for table in tables:
        caption = table.find("caption")
        table_text = table.get_text(separator="\n")
        caption_text = caption.get_text() if caption else ""

        if "TABLE OF CONTENTS" in table_text or "TABLE OF CONTENTS" in caption_text:
            toc_table = table
            break

    if not toc_table:
        print(f"❌ {name}: TOC not found in HTML.")
        return None

    sections = []

    # Extract TOC text and clean it up
    raw_toc_text = toc_table.get_text(separator="\n").strip()

    # Remove the header if it appears at the start
    raw_toc_text = re.sub(r"^\s*3M COMPANY ANNUAL REPORT ON FORM 10K TABLE OF CONTENTS PAGE\s*", "", raw_toc_text, flags=re.IGNORECASE)

    # Split into raw lines (handling incorrect line breaks)
    toc_lines = [
        re.sub(r"[-]+", "", line).strip()  # Remove dashes and extra spaces
        for line in raw_toc_text.split("\n")
        if line.strip()
    ]

    # Advanced regex to split multiple TOC entries on the same line
    toc_entries = []
    for line in toc_lines:
        # Use regex to find multiple sections with page numbers in the same line
        matches = re.findall(r"(.+?)\s+(\d+)", line)
        for match in matches:
            title, page = match
            toc_entries.append({"title": title.strip(), "page": page.strip()})

    # Save TOC data to JSON file
    toc_file = os.path.join(output_dir, f"{name}_toc.json")
    with open(toc_file, "w", encoding="utf-8") as f:
        json.dump(toc_entries, f, indent=4)

    print(f"✅ {name}: TOC extracted and saved to {toc_file}")
    return toc_entries
