import re

def is_valid_entity(text):
    if not text.strip():
        return False  # empty or whitespace

    if not text.isascii():
        return False  # non-ASCII characters

    if re.fullmatch(r'\d+', text):
        return False  # purely numeric

    if re.search(r'https?://', text):
        return False  # contains a URL

    if re.fullmatch(r'[QP]\d+', text):
        return False  # looks like a Wikidata ID

    if not re.search(r'[A-Za-z]', text):
        return False  # must contain at least one letter

    return True

def clean_file(input_file="property_examples.txt", output_file="property_examples_cleaned.txt"):
    print("🔍 Cleaning file (non-English, numeric-only, links, and IDs)...")
    lines_kept = 0
    lines_skipped = 0

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            line = line.strip()
            if not line:
                continue

            try:
                # Example: "Mary P25 Joan, Mary P25 Michael"
                first, second = line.split(", ")
                subj1, pred1, obj1 = first.split(" ", 2)
                subj2, pred2, obj2 = second.split(" ", 2)

                # Validate subject and both objects (you may skip predicate checks if using P-ID)
                entities = [subj1, obj1, obj2]

                if not all(is_valid_entity(e) for e in entities):
                    lines_skipped += 1
                    continue

                outfile.write(line + "\n")
                lines_kept += 1
            except ValueError:
                lines_skipped += 1
                continue

    print(f"✅ Cleaning complete.")
    print(f"✔️  Lines kept: {lines_kept}")
    print(f"❌ Lines removed: {lines_skipped}")
    print(f"📄 Cleaned file saved to: {output_file}")

# Run
if __name__ == "__main__":
    clean_file()

