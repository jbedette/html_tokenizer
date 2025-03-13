from bs4 import BeautifulSoup
import os
import json

def find_table_of_contents(html_content, name):
    """Extracts TOC from 10-K HTML filings using BeautifulSoup and saves it to JSON."""
    soup = BeautifulSoup(html_content, "lxml")

    # Ensure TOC output directory exists
    output_dir = "tocs"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Locate TOC by finding the "TABLE OF CONTENTS" text
    toc_table = None
    for table in soup.find_all("table"):
        if "TABLE OF CONTENTS" in table.get_text():
            toc_table = table
            break

    if not toc_table:
        print(f"❌ {name}: TOC not found in HTML.")

        # Save the full HTML content to a file for debugging
        debug_file = "debug_toc_missing.txt"
        with open(debug_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== {name}: TOC not found ===\n")
            f.write(html_content)  # Save full HTML content
            f.write("\n" + "="*50 + "\n")
        
        return None

    sections = []
    
    # Step 2: Extract section titles and page numbers from TOC
    for row in toc_table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) < 2:
            continue  # Skip malformed rows

        # Section title is inside <a> tag in one of the columns
        section_link = columns[0].find("a")
        section_title = section_link.get_text(strip=True) if section_link else columns[0].get_text(strip=True)
        
        # Extract page number from the last column
        page_number = columns[-1].get_text(strip=True)

        # Extract the section ID from href if available
        section_id = section_link["href"] if section_link else None

        # Ensure it's a valid section (ignoring blank rows)
        if section_title:
            sections.append({
                "title": section_title,
                "page": page_number if page_number else None,
                "id": section_id
            })

    # Step 3: Save TOC as JSON
    output_file = os.path.join(output_dir, f"{name}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"name": name, "sections": sections}, f, indent=4)

    print(f"📁 {name}: TOC saved to {output_file}")

    return sections if sections else None


# import re
# import os
# import json


# def find_table_of_contents(text, name):
#     """Extracts the Table of Contents (TOC) dynamically from 10-K filings and saves it to JSON."""
#     lines = text.split("\n")

#     # Ensure TOC output directory exists
#     output_dir = "tocs"
#     os.makedirs(output_dir, exist_ok=True)

#     # Step 1: Locate the TOC start by searching for "TABLE OF CONTENTS"
#     toc_start = None
#     toc_end = None
#     toc_lines = []

#     for i, line in enumerate(lines):
#         if re.search(r'\bTABLE\s+OF\s+CONTENTS\b|\bTABLE\s+CONTENTS\b', line, re.IGNORECASE):
#             toc_start = i
#             break  # Stop at the first occurrence

#     if toc_start is None:
#         print(f"❌ {name}: TOC not found in text.")
#         return None

#     # Step 2: Extract TOC lines until we reach non-section text
#     for i in range(toc_start + 1, len(lines)):
#         line = lines[i].strip()

#         # Stop if we reach unrelated content (e.g., Signatures, Appendices)
#         if re.search(r'\bSignatures\b|\bExhibits\b', line, re.IGNORECASE):
#             toc_end = i
#             break

#         # Detect section numbers like "Item 1.", "Item 1A."
#         if re.match(r'Item\s*\d+[A-Z]?\.', line, re.IGNORECASE) or re.match(r'Part\s*[IVX]+', line, re.IGNORECASE):
#             toc_lines.append(line)

#     if not toc_lines:
#         print(f"❌ {name}: TOC extraction failed: No valid section entries found.")
#         return None

#     print(f"✅ {name}: TOC found")

#     # Step 3: Parse extracted TOC lines into structured data
#     sections = []
#     for line in toc_lines:
#         match = re.match(r'Item\s*(\d+[A-Z]?)\.\s*(.+?)\s*(\d+)?$', line.strip())
#         if match:
#             section_number, section_title, page_number = match.groups()
#             sections.append({
#                 "item": section_number,
#                 "title": section_title,
#                 "page": page_number if page_number else None
#             })

#     # Step 4: Save TOC data as JSON
#     output_file = os.path.join(output_dir, f"{name}.json")
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump({"name": name, "sections": sections}, f, indent=4)

#     print(f"📁 {name}: TOC saved to {output_file}")

#     return sections if sections else None
