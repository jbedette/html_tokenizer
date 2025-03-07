import re
import os
import json

def find_table_of_contents(text, name):
    """Extracts the Table of Contents (TOC) dynamically from 10-K filings and saves it to JSON."""
    lines = text.split("\n")

    # Ensure TOC output directory exists
    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Locate the TOC start by searching for "TABLE OF CONTENTS"
    toc_start = None
    toc_end = None
    toc_lines = []

    for i, line in enumerate(lines):
        if re.search(r'\bTABLE\s+OF\s+CONTENTS\b|\bTABLE\s+CONTENTS\b', line, re.IGNORECASE):
            toc_start = i
            break  # Stop at the first occurrence

    if toc_start is None:
        print(f"❌ {name}: TOC not found in text.")
        return None

    # Step 2: Extract TOC lines until we reach non-section text
    for i in range(toc_start + 1, len(lines)):
        line = lines[i].strip()

        # Stop if we reach unrelated content (e.g., Signatures, Appendices)
        if re.search(r'\bSignatures\b|\bExhibits\b', line, re.IGNORECASE):
            toc_end = i
            break

        # Detect section numbers like "Item 1.", "Item 1A."
        if re.match(r'Item\s*\d+[A-Z]?\.', line, re.IGNORECASE) or re.match(r'Part\s*[IVX]+', line, re.IGNORECASE):
            toc_lines.append(line)

    if not toc_lines:
        print(f"❌ {name}: TOC extraction failed: No valid section entries found.")
        return None

    print(f"✅ {name}: TOC found")

    # Step 3: Parse extracted TOC lines into structured data
    sections = []
    for line in toc_lines:
        match = re.match(r'Item\s*(\d+[A-Z]?)\.\s*(.+?)\s*(\d+)?$', line.strip())
        if match:
            section_number, section_title, page_number = match.groups()
            sections.append({
                "item": section_number,
                "title": section_title,
                "page": page_number if page_number else None
            })

    # Step 4: Save TOC data as JSON
    output_file = os.path.join(output_dir, f"{name}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"name": name, "sections": sections}, f, indent=4)

    print(f"📁 {name}: TOC saved to {output_file}")

    return sections if sections else None
