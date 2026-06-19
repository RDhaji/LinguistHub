import json
import os

# This processes files and saves them in the SAME folder you are currently looking at
for filename in os.listdir('.'):
    if filename.endswith(".json") and not filename.startswith("structured_"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Logic: If it's a list, structure it. If it's a dict, keep it.
            structured = {}
            if isinstance(data, list):
                structured = {word: {
                    "synonyms": [], 
                    "antonyms": [], 
                    "forms": {"noun": [], "verb": [], "adjective": [], "adverb": []}
                } for word in data}
            else:
                structured = data
            
            # Save right here in the current folder with a "structured_" prefix
            new_name = "structured_" + filename
            with open(new_name, 'w', encoding='utf-8') as f:
                json.dump(structured, f, indent=4, ensure_ascii=False)
            
            print(f"Created: {new_name}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("Done! Look at your file explorer, you will see the new files right there.")