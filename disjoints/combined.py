import random

# File paths
file1 = 'contradictions_subclass_only_labels.txt'
file2 = 'no_contradictions_subclass_only_labels.txt'
output_scrambled = 'mixed_output.txt'
output_tagged = 'mixed_output_tagged.txt'

# Read and label lines
with open(file1, 'r', encoding='utf-8') as f1:
    lines1 = [(line, 'yes') for line in f1.readlines()]  # 'yes' for file1

with open(file2, 'r', encoding='utf-8') as f2:
    lines2 = [(line, 'no') for line in f2.readlines()]   # 'no' for file2

# Combine and shuffle
combined = lines1 + lines2
random.shuffle(combined)

# Write scrambled lines
with open(output_scrambled, 'w', encoding='utf-8') as out:
    for line, _ in combined:
        out.write(line)

# Write tagged lines
with open(output_tagged, 'w', encoding='utf-8') as out_tagged:
    for line, tag in combined:
        line_clean = line.rstrip('\n')  # Remove trailing newline
        out_tagged.write(f'{line_clean}\t{tag}\n')

