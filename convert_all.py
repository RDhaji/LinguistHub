import json
import os

# This script converts flat JSON lists to the Object Map structure used in your project.
def convert_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if file is already converted (dictionary) or flat list
    if isinstance(data, dict):
        return # Already structured
        
    # Convert flat list [a, b, c] -> {a: {...}, b: {...}, c: {...}}
    structured_data = {}
    for word in data:
        structured_data[word] = {
            "synonyms": [],
            "antonyms": [],
            "forms": {
                "noun": [],
                "verb": [],
                "adjective": [],
                "adverb": []
            }
        }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=4, ensure_ascii=False)

# Process all json files in the folder
for filename in os.listdir('.'):
    if filename.endswith(".json"):
        print(f"Converting {filename}...")
        convert_file(filename)

print("All files converted to object-map structure.")
