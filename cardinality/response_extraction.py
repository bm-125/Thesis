import re

def extract_answers(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Skip header line
    raw_data = lines[1:]

    # Normalize entries
    entries = []
    current_entry = ''
    for line in raw_data:
        if re.match(r'^\d+,', line):  # New row starts
            if current_entry:
                entries.append(current_entry)
            current_entry = line.strip()
        else:
            current_entry += ' ' + line.strip()
    if current_entry:
        entries.append(current_entry)

    answers = []
    unknown_cases = []
    for entry in entries:
        parts = entry.split(',')
        if len(parts) >= 4:
            response = ','.join(parts[3:]).strip()
            match = re.search(r'\b(Yes|No)\b', response, re.IGNORECASE)
            if match:
                answers.append(match.group(1).capitalize())
            else:
                answers.append('No')
                unknown_cases.append(entry)
        else:
            answers.append('Unknown')
            unknown_cases.append(entry)

    # Write answers to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for answer in answers:
            outfile.write(answer + '\n')

    # Print unknown cases
    if unknown_cases:
        print("Unknown cases found:")
        for case in unknown_cases:
            print(case)


# Usage
extract_answers('results_qwen2_cardinality.csv', 'output_qwen2_cardi.txt')
