import re

# Pattern to detect Wikidata Q-IDs
qid_pattern = re.compile(r'\bQ\d+\b')

# Files to process
files = [
    "contradictions_full_statements_labels.txt",
    "contradictions_subclass_only_labels.txt"
]

for filename in files:
    print(f"🧹 Cleaning {filename}...")
    
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Keep only lines without Q-IDs
    cleaned_lines = [line for line in lines if not qid_pattern.search(line)]

    # Overwrite the original file
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    print(f"✅ Removed {len(lines) - len(cleaned_lines)} lines from {filename}")
