from bs4 import BeautifulSoup
import os
import json
import re

def find_table_of_contents(html_content, name):
    """Extracts TOC from 10-K HTML filings and structures them by Parts."""
    soup = BeautifulSoup(html_content, "html.parser")  # Use 'html.parser' for better parsing

    # Ensure output directory exists
    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    debug_file = f"debug_toc_{name}.txt"

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

    # Extract TOC text and clean it up
    raw_toc_text = toc_table.get_text(separator="\n").strip()

    # Save the raw TOC text for debugging
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write("=== RAW TOC TEXT ===\n")
        f.write(raw_toc_text + "\n\n")

    # Remove unnecessary headers (dynamic for any 10-K)
    raw_toc_text = re.sub(r"(?i)^.*?TABLE OF CONTENTS\s*", "", raw_toc_text)

    # **Force restore missing line breaks** between ITEMs using regex
    raw_toc_text = re.sub(r"(ITEM\s+\d+[A-Z]?)", r"\n\1", raw_toc_text)

    # Now split into proper lines
    toc_lines = [
        re.sub(r"[-]+", "", line).strip()  # Remove excessive dashes
        for line in raw_toc_text.split("\n")
        if line.strip()
    ]

    # Save cleaned TOC lines for debugging
    with open(debug_file, "a", encoding="utf-8") as f:
        f.write("=== CLEANED TOC LINES (With Fix) ===\n")
        for line in toc_lines:
            f.write(line + "\n")

    toc_entries = []
    current_part = None  # Track current part (e.g., PART I, PART II)

    for line in toc_lines:
        print(f"Processing line: {line}")  # Debugging print statement

        # Match "PART X" sections
        part_match = re.match(r"^(PART\s+[IVXLCDM]+)", line, re.IGNORECASE)
        if part_match:
            current_part = part_match.group(1).strip()
            print(f"Detected PART: {current_part}")
            continue  # Skip adding "PART X" itself to the list

        # Match "ITEM X -- Title" pattern (flexible to handle variations)
        item_match = re.match(r"^(ITEM\s+\d+[A-Z]?)\s*[-–—]*\s*(.+?)(?:\s+\d+)?$", line, re.IGNORECASE)
        if item_match:
            item_number = item_match.group(1).strip()
            item_title = item_match.group(2).strip()

            print(f"Extracted Item: {item_number} - {item_title}")  # Debugging print

            entry = {
                "part": current_part if current_part else "UNKNOWN PART",
                "item": item_number,
                "title": item_title
            }
            toc_entries.append(entry)
            continue  # Skip further processing of this line

        # Catch entries like "Index to Financial Statements" that don’t have ITEM numbers
        if current_part and not re.search(r"ITEM\s+\d+", line, re.IGNORECASE):
            print(f"Adding Index Entry: {line}")  # Debugging print
            toc_entries.append({"part": current_part, "item": None, "title": line})

    # Save the cleaned TOC data to JSON file
    toc_file = os.path.join(output_dir, f"{name}_toc.json")
    with open(toc_file, "w", encoding="utf-8") as f:
        json.dump(toc_entries, f, indent=4)

    print(f"✅ {name}: TOC extracted and saved to {toc_file}")
    print(f"📄 Debugging file saved: {debug_file}")

    return toc_entries
