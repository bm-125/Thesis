import csv
import requests

# Input and output file paths
input_file = 'contradictions.csv'  # Replace with your actual CSV file name
output_file = 'output_labels_contradictions.txt'

# Function to extract Wikidata ID from full URI
def extract_id(uri):
    if 'wikidata.org/entity/' in uri:
        return uri.split('/')[-1]
    return None

# Function to fetch labels from Wikidata
def fetch_labels(entities):
    labels = {}
    chunks = [entities[i:i+50] for i in range(0, len(entities), 50)]  # Query in chunks
    for chunk in chunks:
        ids = '|'.join(chunk)
        url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids}&format=json&props=labels&languages=en'
        r = requests.get(url).json()
        for eid in r.get('entities', {}):
            label = r['entities'][eid].get('labels', {}).get('en', {}).get('value')
            if label:
                labels[eid] = label
    return labels

# Read data and collect IDs
all_ids = set()
rows = []

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        property_id = row['property']
        item_id = extract_id(row['item'])
        value1_id = extract_id(row['value1'])
        value2_id = extract_id(row['value2'])
        all_ids.update([property_id, item_id])
        if value1_id: all_ids.add(value1_id)
        if value2_id: all_ids.add(value2_id)
        rows.append((item_id, property_id, value1_id, value2_id))

# Get labels
labels = fetch_labels(list(all_ids))

# Write to output file, skip if any label is missing
with open(output_file, 'w', encoding='utf-8') as f:
    for item, prop, val1, val2 in rows:
        if not all([item, prop, val1, val2]):
            continue  # Skip if any ID is None

        label_item = labels.get(item)
        label_prop = labels.get(prop)
        label_val1 = labels.get(val1)
        label_val2 = labels.get(val2)

        # Skip if any label is missing
        if not all([label_item, label_prop, label_val1, label_val2]):
            continue

        statement1 = f"{label_item} {label_prop} {label_val1}"
        statement2 = f"{label_item} {label_prop} {label_val2}"
        f.write(f"{statement1}, {statement2}\n")

