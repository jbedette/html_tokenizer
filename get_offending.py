# import os
# import shutil

# # Define paths
# log_file = "cleaned_10k_reports/missing_toc.log"
# source_base = "sec-edgar-filings"
# destination_folder = "offending"

# # Ensure destination folder exists
# os.makedirs(destination_folder, exist_ok=True)

# # Process the log file
# with open(log_file, "r", encoding="utf-8") as log:
#     for line in log:
#         fn = line.strip()  # Remove leading/trailing whitespace

#         if not fn:  # Skip empty lines
#             continue

#         # Extract ticker (tkr) and filing from filename
#         base_name = os.path.basename(fn)
#         parts = base_name.split("_", 1)

#         if len(parts) < 2:
#             print(f"Skipping invalid filename: {fn}")
#             continue

#         tkr, filing = parts[0], parts[1].split(".",1)[0]

#         # Construct full_submission.txt path
#         source_file = os.path.join(source_base, tkr, "10-K", filing, "full_submission.txt")

#         if os.path.exists(source_file):
#             # Define destination file path
#             dest_file = os.path.join(destination_folder, base_name)

#             # Copy the file
#             shutil.copy(source_file, dest_file)
#             print(f"Copied: {source_file} -> {dest_file}")
#         else:
#             print(f"Missing file: {source_file}")
import os
import shutil

# Define paths
log_file = "./cleaned_10k_reports/missing_toc.log"
# source_base = "./sec-edgar-filings"
source_base = "/Users/jbedette/code/personal/html_tokenizer/sec-edgar-filings"
destination_folder = "./offending"

# Ensure destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Process the log file
with open(log_file, "r", encoding="utf-8") as log:
    for line in log:
        fn = line.strip()  # Remove leading/trailing whitespace

        if not fn:  # Skip empty lines
            continue

        # Extract ticker (tkr) and filing from filename
        base_name = os.path.basename(fn)
        parts = base_name.split("_", 1)

        if len(parts) < 2:
            print(f"Skipping invalid filename: {fn}")
            continue

        tkr, filing = parts[0], parts[1].split(".", 1)[0]
        filing = filing.strip()  # Ensure no trailing spaces or newline characters

        # Construct full_submission.txt path
        source_file = os.path.join(source_base, tkr, "10-K", filing, "full-submission.txt")
        # source_file = "/Users/jbedette/code/personal/html_tokenizer/sec-edgar-filings/MMM/10-K/0001104659-05-008057/full_submission.txt"

        # Debugging output
        print(f"Checking file: {source_file} (Exists: {os.path.exists(source_file)})")

        if os.path.exists(source_file):
            # Define destination file path
            dest_file = os.path.join(destination_folder, base_name)

            # Copy the file
            shutil.copy(source_file, dest_file)
            print(f"Copied: {source_file} -> {dest_file}")
        else:
            print(f"Missing file: {source_file}")

# /Users/jbedette/code/personal/html_tokenizer/sec-edgar-filings/MMM/10-K/0001104659-05-008057/full_submission.txt