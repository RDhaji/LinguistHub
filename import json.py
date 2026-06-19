import json
import os

# Create an 'output' folder if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

def convert_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # [Your conversion logic here]
    structured_data = {word: {"synonyms": [], "antonyms": [], "forms": {"noun": [], "verb": [], "adjective": [], "adverb": []}} for word in data}
    
    # Save to the new 'output' folder instead of overwriting
    with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=4, ensure_ascii=False)

# Process files
for filename in os.listdir('.'):
    if filename.endswith(".json") and filename != 'convert_all.py':
        print(f"Converting {filename} to output/ folder...")
        convert_file(filename)