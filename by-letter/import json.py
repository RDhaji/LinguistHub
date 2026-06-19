import json
import os

# Define the target subfolder name
subfolder_name = "by-letter"
output_dir = os.path.join(os.getcwd(), subfolder_name)

# Create the folder if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created folder: {output_dir}")

# Process files
for filename in os.listdir(os.getcwd()):
    # Only process .json files and ignore the current script and the target folder
    if filename.endswith(".json") and filename != "convert_and_organize.py" and filename != subfolder_name:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to "Gold Standard" Object Map
            # If data is a list, convert it. If it's already a dict, keep it as is.
            structured = {}
            if isinstance(data, list):
                structured = {word: {
                    "synonyms": [], 
                    "antonyms": [], 
                    "forms": {"noun": [], "verb": [], "adjective": [], "adverb": []}
                } for word in data}
            else:
                structured = data
            
            # Save to the new nested by-letter folder
            new_file_path = os.path.join(output_dir, filename)
            with open(new_file_path, 'w', encoding='utf-8') as f:
                json.dump(structured, f, indent=4, ensure_ascii=False)
            
            print(f"Successfully processed: {filename} -> {subfolder_name}/{filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("All done! Check your 'by-letter/by-letter/' folder.")