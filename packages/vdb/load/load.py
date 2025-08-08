import re
import requests
from bs4 import BeautifulSoup
import vdb

USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB.
Start with * to do a vector search in the DB.
Start with ! to remove text with a substring.
Start with https:// to load and index web content.
"""

def simple_tokenize(text):
    # Split text into words using regex, excluding punctuation
    return re.findall(r'\b\w+\b', text)

def load(args):
    collection = args.get("COLLECTION", "default")
    out = f"{USAGE}Current collection is {collection}\n"
    inp = str(args.get('input', ""))
    db = vdb.VectorDB(args)

    if inp.startswith("*"):
        if len(inp) == 1:
            out = "Please specify a search string."
        else:
            res = db.vector_search(inp[1:])
            if len(res) > 0:
                out = "Found:\n"
                for i in res:
                    out += f"({i[0]:.2f}) {i[1]}\n"
            else:
                out = "Not found."

    elif inp.startswith("!"):
        count = db.remove_by_substring(inp[1:])
        out = f"Deleted {count} records."

    elif inp.startswith("https://"):
        try:
            response = requests.get(inp)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract visible text from HTML
            text = soup.get_text(separator=' ', strip=True)

            # Tokenize the extracted text
            tokens = simple_tokenize(text)

            # Combine into reasonably sized chunks (e.g., 100 words each)
            chunk_size = 100
            chunks = [
                " ".join(tokens[i:i+chunk_size])
                for i in range(0, len(tokens), chunk_size)
            ]

            inserted_ids = []
            for chunk in chunks:
                if chunk.strip():  # Avoid inserting empty chunks
                    res = db.insert(chunk)
                    inserted_ids.extend(res.get("ids", []))

            out = f"Inserted {len(inserted_ids)} text chunks from the URL."

        except Exception as e:
            out = f"Failed to fetch or process URL: {e}"

    elif inp != '':
        res = db.insert(inp)
        out = "Inserted " 
        out += " ".join([str(x) for x in res.get("ids", [])])

    return {"output": out}
