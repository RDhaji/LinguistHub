import json
import nltk
import os
from nltk.corpus import wordnet as wn

# Ensure wordnet is downloaded
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def get_pos(word):
    synsets = wn.synsets(word)
    pos_map = {'noun': [], 'verb': [], 'adjective': [], 'adverb': []}
    for syn in synsets:
        pos = syn.pos()
        if pos == 'n': pos_map['noun'].append(word)
        elif pos == 'v': pos_map['verb'].append(word)
        elif pos == 'a' or pos == 's': pos_map['adjective'].append(word)
        elif pos == 'r': pos_map['adverb'].append(word)
    # Remove duplicates
    for key in pos_map:
        pos_map[key] = list(set(pos_map[key]))
    return pos_map

# Loop through all files that start with 'structured_'
for filename in os.listdir('.'):
    if filename.startswith("structured_") and filename.endswith(".json"):
        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Update each word with POS data
        for word in data:
            data[word]['forms'] = get_pos(word)

        # Save back to the same file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

print("All files updated successfully!")