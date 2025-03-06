from bs4 import BeautifulSoup
# html5lib 
# def clean_html(html_content):
#     soup = BeautifulSoup(html_content, "html5lib")  # Handles broken HTML
#     return soup.get_text(separator=" ")  # Extracts text with spacing

# lxml
def clean_html(html_content):
    try:
        # Use lxml if available (faster and handles large files well)
        soup = BeautifulSoup(html_content, "lxml")
    except:
        # Fallback to built-in html.parser if lxml is not installed
        soup = BeautifulSoup(html_content, "html.parser")
    
    return soup.get_text(separator=" ")
