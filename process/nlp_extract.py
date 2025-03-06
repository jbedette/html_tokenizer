import spacy
import re
from bs4 import BeautifulSoup
nlp = spacy.load("en_core_web_sm")

def find_table_of_contents(text, name):
    """Extracts the Table of Contents (TOC) dynamically from 10-K filings."""
    lines = text.split("\n")

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
            sections.append((section_number, section_title, page_number))

    return sections if sections else None


# def find_table_of_contents(html_content):
#     """Extracts the Table of Contents section from the HTML report."""
#     soup = BeautifulSoup(html_content, "lxml")

#     # Step 1: Locate the TOC table
#     toc_table = None
#     for table in soup.find_all("table"):
#         if "TABLE OF CONTENTS" in table.get_text():
#             toc_table = table
#             break

#     if not toc_table:
#         # print("❌ TOC not found in HTML.")
#         return None

#     # Step 2: Extract section titles and their links
#     sections = []
#     for row in toc_table.find_all("tr"):
#         columns = row.find_all("td")
#         if len(columns) < 4:
#             continue  # Ignore empty or malformed rows

#         # Section number (e.g., "Item 1.")
#         section_number = columns[1].get_text(strip=True)
#         # Section title (e.g., "Business")
#         section_title = columns[2].get_text(strip=True)
#         # Page number (last column, optional)
#         page_number = columns[3].get_text(strip=True) if len(columns) > 3 else ""

#         # Extract link (if available)
#         link = columns[2].find("a")
#         section_id = link["href"] if link else None

#         # Ensure valid section
#         if section_number and section_title:
#             sections.append((section_number, section_title, section_id, page_number))

#     return sections

# def find_table_of_contents(text):
#     """Identifies and extracts the Table of Contents from a 10-K filing."""
#     lines = text.split("\n")
#     toc_start = None
#     toc_end = None
#     toc_lines = []

#     # Regex pattern to match structured section numbers (e.g., "1.", "1.1", "I.", "A.")
#     section_pattern = re.compile(r"^\s*(\d+\.|\d+\.\d+|[IVXLCDM]+\.)\s+\S+")

#     for i, line in enumerate(lines):
#         clean_line = line.strip().lower()

#         # Step 1: Find the **first** "Table of Contents" that isn't a stray mention
#         if "table of contents" in clean_line and toc_start is None:
#             toc_start = i
#             continue  # Skip to next line

#         # Step 2: Identify numbered sections (likely TOC entries)
#         if toc_start is not None and section_pattern.match(line):
#             toc_lines.append(line.strip())

#         # Step 3: Detect TOC end (a blank line or non-section text)
#         elif toc_start is not None and len(line.strip()) == 0:
#             toc_end = i
#             break

#     # If we found TOC and valid sections, return them
#     if toc_start is not None and toc_lines:
#         return toc_lines
#     else:
#         return None  # TOC not found

def chunk_text(text, chunk_size=500000):  # Adjust chunk size as needed
    """Splits text into smaller chunks for spaCy processing."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def extract_sections(html_content,name):
    """Uses TOC to split the document into sections."""
    soup = BeautifulSoup(html_content, "lxml")
    toc_sections = find_table_of_contents(html_content,name)

    if not toc_sections:
        print(f"❌❌ {name}: TOC not found, falling back to full document extraction.")
        return {"Full Document": soup.get_text()}

    extracted_sections = {}
    current_section = None
    buffer = []

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "div", "p"]):
        text = tag.get_text(strip=True)

        # Check if text matches TOC section
        for section_number, section_title, section_id, _ in toc_sections:
            if section_title.lower() in text.lower():
                # Store previous section
                if current_section:
                    extracted_sections[current_section] = "\n".join(buffer)
                # Start new section
                current_section = section_title
                buffer = []
                break

        buffer.append(text)

    # Save last section
    if current_section:
        extracted_sections[current_section] = "\n".join(buffer)

    return extracted_sections


# def extract_sections(text,name):
#     """Extracts sections dynamically based on TOC, processing in chunks if needed."""
#     extracted_text = []

#     for chunk in chunk_text(text):
#         doc = nlp(chunk)  # Process in smaller pieces
#         clean_text = " ".join([token.text for token in doc if not token.is_punct])
#         extracted_text.append(clean_text)

#     # Join chunks back together
#     full_text = "\n".join(extracted_text)

#     # Step 1: Detect TOC sections
#     toc_sections = find_table_of_contents(full_text)

#     if not toc_sections:
#         print(f"❌ {name}: TOC not found, falling back to full document extraction.")
#         return {"Full Document": full_text}

#     extracted_sections = {}
#     current_section = None
#     buffer = []

#     # Step 2: Extract text under each section heading
#     lines = full_text.split("\n")
#     for line in lines:
#         if any(sec.lower() in line.lower() for sec in toc_sections):
#             if current_section:
#                 extracted_sections[current_section] = "\n".join(buffer)
#             current_section = line.strip()
#             buffer = []
#         else:
#             buffer.append(line)

#     if current_section:
#         extracted_sections[current_section] = "\n".join(buffer)

#     return extracted_sections