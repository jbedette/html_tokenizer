import magic

def detect_format(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    
    if "html" in file_type:
        return "html"
    elif "text" in file_type:
        return "text"
    else:
        return "unknown"
