import os
import json

# Specify the folder containing the JSON files
FOLDER_PATH = "gpt_process"

def is_valid_json(file_path):
    """Check if a file contains valid JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json.load(file)  # Try parsing JSON
        return True
    except json.JSONDecodeError as e:
        print(f"⚠️ Invalid JSON in {file_path}: {e}")
        return False

def clean_file_content(file_path):
    """Reads a JSON file, performs replacements, and writes back the cleaned content."""
    if not is_valid_json(file_path):
        return  # Skip processing invalid JSON files

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Perform replacements
    content = content.replace("\\n", "\n")  # Replace escaped newlines with real newlines
    content = content.replace("\t", "    ")  # Replace tab with 4 spaces
    content = content.replace("\\\"", "\"")  # Replace escaped quotes with real quotes
    content = content.replace("```", "''")   # Replace triple backticks with two single quotes

    # Write back the cleaned content
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"✅ Cleaned: {file_path}")

def process_folder(folder_path):
    """Processes all JSON files in the given folder."""
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' does not exist.")
        return

    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]  # ✅ Only process JSON files
    if not files:
        print(f"📂 No JSON files found in '{folder_path}'.")
        return

    print(f"🔍 Processing {len(files)} JSON files in '{folder_path}'...\n")

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        clean_file_content(file_path)

    print("\n🎉 All valid JSON files processed successfully!")

# Run the script
process_folder(FOLDER_PATH)
