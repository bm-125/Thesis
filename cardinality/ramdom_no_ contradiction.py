import random
import re

def load_property_labels(file_path):
    property_labels = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                pid, label = parts[0], parts[1]
                property_labels[pid] = label
    return property_labels

def is_valid_phrase(text):
    # All words must be alphabetic
    return all(word.isalpha() for word in text.split())

def sample_and_replace(input_file, property_file, output_file, sample_size=476):
    print("🔍 Loading property labels...")
    property_labels = load_property_labels(property_file)

    print("📂 Reading cleaned statements...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]

    print("🧹 Filtering valid lines...")
    valid_lines = []
    for line in all_lines:
        try:
            first, second = line.split(", ")
            subj1, pred1, obj1 = first.split(" ", 2)
            subj2, pred2, obj2 = second.split(" ", 2)

            # Check label exists
            if pred1 not in property_labels:
                continue

            # Ensure all phrases are alphabetic (no numbers or mixed words)
            if not all(map(is_valid_phrase, [subj1, obj1, obj2])):
                continue

            valid_lines.append((subj1, pred1, obj1, obj2))
        except ValueError:
            continue

    print(f"🔢 Valid lines after filtering: {len(valid_lines)}")
    if len(valid_lines) < sample_size:
        raise ValueError(f"Not enough valid lines to sample {sample_size} (only {len(valid_lines)} available).")

    print(f"🎲 Sampling {sample_size} random lines...")
    sampled = random.sample(valid_lines, sample_size)

    print("✏️ Replacing property IDs with labels and writing output...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for subj, prop_id, obj1, obj2 in sampled:
            label = property_labels[prop_id]
            line = f"{subj} {label} {obj1}, {subj} {label} {obj2}"
            f.write(line + "\n")

    print(f"✅ Done. Output saved to '{output_file}'.")

# Run
if __name__ == "__main__":
    sample_and_replace(
        input_file="property_examples_cleaned.txt",
        property_file="filtered_no_svc.txt",
        output_file="sampled_476_lines.txt",
        sample_size=476
    )

