from bs4 import BeautifulSoup
import os
import json
import re

def list_all_files(directory):
    """Lists all files in the given directory."""
    print("\n📂 Available Files for Processing:")
    for file in os.listdir(directory):
        print(f" - {file}")
    print("\n")

def detect_file_type(file_path):
    """Check if a file is HTML or plain text based on extension and content."""
    if file_path.lower().endswith((".html", ".htm")):
        return "html"
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
        return "html" if "<html" in first_line.lower() else "text"
    return "unknown"

def extract_toc_original(html_content, name):
    """First attempt: Extract TOC using the original method."""
    soup = BeautifulSoup(html_content, "lxml")

    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    toc_table = None
    for table in soup.find_all("table"):
        if "TABLE OF CONTENTS" in table.get_text():
            toc_table = table
            break

    if not toc_table:
        print(f"❌ {name}: TOC not found using original method.")
        return None

    sections = []
    for row in toc_table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) < 2:
            continue  # Skip malformed rows

        section_link = columns[0].find("a")
        section_title = section_link.get_text(strip=True) if section_link else columns[0].get_text(strip=True)
        section_id = section_link["href"] if section_link else None

        if section_title:
            sections.append({"title": section_title, "id": section_id})

    output_file = os.path.join(output_dir, f"{name}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"name": name, "sections": sections}, f, indent=4)

    print(f"✅ {name}: TOC extracted using original method and saved to {output_file}")
    return sections if sections else None

def extract_toc_refined(html_content, name):
    """Fallback method: Extract TOC using the refined method."""
    soup = BeautifulSoup(html_content, "html.parser")

    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    debug_file = f"debug_toc_{name}.txt"
    tables = soup.find_all("table")

    toc_table = None
    for table in tables:
        caption = table.find("caption")
        table_text = table.get_text(separator="\n")
        caption_text = caption.get_text() if caption else ""

        if "TABLE OF CONTENTS" in table_text or "TABLE OF CONTENTS" in caption_text:
            toc_table = table
            break

    if not toc_table:
        print(f"❌ {name}: TOC not found using refined method.")
        return None

    raw_toc_text = toc_table.get_text(separator="\n").strip()
    raw_toc_text = re.sub(r"(?i)^.*?TABLE OF CONTENTS\s*", "", raw_toc_text)
    raw_toc_text = re.sub(r"(ITEM\s+\d+[A-Z.]*)", r"\n\1", raw_toc_text)

    toc_lines = [re.sub(r"[-]+", "", line).strip() for line in raw_toc_text.split("\n") if line.strip()]

    with open(debug_file, "w", encoding="utf-8") as f:
        f.write("=== CLEANED TOC LINES ===\n")
        for line in toc_lines:
            f.write(line + "\n")

    toc_entries = []
    current_part = None

    for line in toc_lines:
        part_match = re.match(r"^(PART\s+[IVXLCDM]+)", line, re.IGNORECASE)
        if part_match:
            current_part = part_match.group(1).strip()
            continue

        item_match = re.match(r"^(ITEM\s+\d+[A-Z.]*)\s*[-–—]*\s*(.+?)(?:\s+\d+)?$", line, re.IGNORECASE)
        if item_match:
            item_number = item_match.group(1).strip()
            item_title = item_match.group(2).strip()
            toc_entries.append({"part": current_part if current_part else "UNKNOWN PART", "item": item_number, "title": item_title})
            continue

        if current_part and not re.search(r"ITEM\s+\d+", line, re.IGNORECASE):
            toc_entries.append({"part": current_part, "item": None, "title": line})

    output_file = os.path.join(output_dir, f"{name}_refined.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(toc_entries, f, indent=4)

    print(f"✅ {name}: TOC extracted using refined method and saved to {output_file}")
    return toc_entries

def process_10k_files(directory):
    """Processes all 10-K files in a directory."""
    list_all_files(directory)

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        file_type = detect_file_type(file_path)

        if file_type == "html":
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            sections = extract_toc_original(html_content, file_name)
            if sections:
                continue  # ✅ Use original method if successful

            print(f"🔄 Falling back to refined method for {file_name}...")
            extract_toc_refined(html_content, file_name)

        elif file_type == "text":
            print(f"⚠ {file_name}: This appears to be plain text, not HTML. Consider converting it.")
        else:
            print(f"🚨 Skipping {file_name}: Unknown file type.")


def find_table_of_contents(html_content, name):
    """Runs the original method first, then falls back to the refined method if needed."""
    sections = extract_toc_original(html_content, name)
    
    if sections:
        return sections  # ✅ Use original method if successful

    print(f"🔄 Falling back to refined method for {name}...")
    return extract_toc_refined(html_content, name)
