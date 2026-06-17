"""
LinguistHub — WordNet Enrichment Script
========================================
Converts flat letter-indexed word list JSON files into structured
JSON with synonyms, antonyms, and POS-grouped word forms.

Requirements:
    pip install nltk

Usage:
    python enrichwordlist.py

Input:  ./by-letter/a.json, b.json ... z.json  (flat string arrays)
Output: ./by-letter-enriched/a.json, b.json ... z.json  (structured objects)
"""

import json
import os
import sys

# ── 1. Install & download NLTK WordNet ───────────────────────────────────────
try:
    import nltk
    from nltk.corpus import wordnet as wn
    from nltk.stem import WordNetLemmatizer
except ImportError:
    print("NLTK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk
    from nltk.corpus import wordnet as wn
    from nltk.stem import WordNetLemmatizer

# Download WordNet data (only needed once — safe to re-run)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()

# ── 2. Configuration ──────────────────────────────────────────────────────────
INPUT_DIR  = "./by-letter"           # folder with your current flat JSON files
OUTPUT_DIR = "./by-letterenriched"  # folder for enriched output files
os.makedirs(OUTPUT_DIR, exist_ok=True)

# WordNet POS tag → matrix column name
POS_MAP = {
    wn.NOUN: "noun",
    wn.VERB: "verb",
    wn.ADJ:  "adjective",
    wn.ADV:  "adverb",
}

# ── 3. Core enrichment function ───────────────────────────────────────────────
def enrichword(word):
    """
    Look up a word in WordNet and return structured data:
    {
        "synonyms":  [...],
        "antonyms":  [...],
        "forms": {
            "noun":      [...],
            "verb":      [...],
            "adjective": [...],
            "adverb":    [...]
        }
    }
    Returns None if WordNet has no entry for this word.
    """
    synsets = wn.synsets(word)
    if not synsets:
        return None

    synonyms  = set()
    antonyms  = set()
    forms     = {"noun": set(), "verb": set(), "adjective": set(), "adverb": set()}

    for synset in synsets:
        pos_key = POS_MAP.get(synset.pos())

        for lemma in synset.lemmas():
            lemma_name = lemma.name().replace("_", " ")

            # Synonyms — any lemma in the same synset that isn't the word itself
            if lemma_name.lower() != word.lower():
                synonyms.add(lemma_name)

            # Antonyms — direct antonym links
            for ant in lemma.antonyms():
                antonyms.add(ant.name().replace("_", " "))

            # POS-grouped forms
            if pos_key:
                forms[pos_key].add(lemma_name)

        # Also collect morphological derivations (word family)
        for lemma in synset.lemmas():
            for related in lemma.derivationally_related_forms():
                rel_name = related.name().replace("_", " ")
                rel_pos  = POS_MAP.get(related.synset().pos())
                if rel_pos:
                    forms[rel_pos].add(rel_name)

    # Remove the searched word from synonyms (keep it clean)
    synonyms.discard(word.lower())
    synonyms.discard(word.capitalize())

    # Cap synonyms/antonyms at 10 (more than enough for display)
    return {
        "synonyms": sorted(list(synonyms))[:10],
        "antonyms": sorted(list(antonyms))[:10],
        "forms": {
            "noun":      sorted(list(forms["noun"])),
            "verb":      sorted(list(forms["verb"])),
            "adjective": sorted(list(forms["adjective"])),
            "adverb":    sorted(list(forms["adverb"])),
        }
    }

# ── 4. Main loop — process each letter file ───────────────────────────────────
letters = "abcdefghijklmnopqrstuvwxyz"

for letter in letters:
    input_path  = os.path.join(INPUT_DIR,  f"{letter}.json")
    output_path = os.path.join(OUTPUT_DIR, f"{letter}.json")

    if not os.path.exists(input_path):
        print(f"  [{letter.upper()}] — file not found, skipping.")
        continue

    with open(input_path, "r", encoding="utf-8") as f:
        word_list = json.load(f)

    print(f"[{letter.upper()}] Processing {len(word_list)} words...", flush=True)

    enriched = {}
    found    = 0
    skipped  = 0

    for i, word in enumerate(word_list):
        # Progress indicator every 500 words
        if i > 0 and i % 500 == 0:
            print(f"      {i}/{len(word_list)} words done...", flush=True)

        # Skip non-string entries and very short tokens (single letters, 2-char codes)
        if not isinstance(word, str) or len(word) < 3:
            skipped += 1
            continue

        result = enrichword(word)

        if result:
            enriched[word] = result
            found += 1
        # Words with no WordNet entry are simply omitted from the output
        # (they were mostly archaic/technical words that don't need matrix data)

    # Write output as a compact but readable JSON object keyed by word
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, separators=(",", ":"))

    print(f"      ✓ {found} enriched, {skipped} skipped → saved to {output_path}")

print("\n✅ All done! Upload the files in ./by-letter-enriched/ to your GitHub repo.")
print("   Then update your fetch path in index.html from:")
print("   './by-letter/${firstLetter}.json'")
print("   to:")
print("   './by-letter-enriched/${firstLetter}.json'")