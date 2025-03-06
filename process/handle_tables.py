import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

def extract_tables(html_content):
    """Extract tables from an HTML document safely."""
    try:
        # Step 1: Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")

        # Step 2: Extract only <table> elements
        tables = soup.find_all("table")

        # Step 3: Convert each table to a DataFrame safely
        dataframes = []
        for table in tables:
            table_str = str(table)
            
            # Try reading the table, but handle cases where no tables are found
            dfs = pd.read_html(StringIO(table_str), flavor="lxml")
            
            if dfs:  # Ensure there is at least one table found
                dataframes.append(dfs[0])  # Append only the first valid DataFrame

        return dataframes if dataframes else []  # Return list of DataFrames

    except Exception as e:
        print(f"❌ Error extracting tables: {e}")
        return []
