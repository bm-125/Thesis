import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.error
import time

# Load the contradiction data
df = pd.read_csv("valid_subclass_pairs.csv")

# Extract all unique Q-IDs (URIs)
all_entities = set(df["violating_subclass"]) | set(df["disjoint_entity1"]) | set(df["disjoint_entity2"])

# Set up SPARQL wrapper
endpoint = SPARQLWrapper("https://query.wikidata.org/sparql")
endpoint.setReturnFormat(JSON)

# Function to fetch labels with exponential backoff
def fetch_labels(qids, max_retries=5, base_delay=5):
    labels = {}
    batch_size = 50
    qid_list = list(qids)

    for i in range(0, len(qid_list), batch_size):
        batch = qid_list[i:i + batch_size]
        values = " ".join(f"wd:{qid.split('/')[-1]}" for qid in batch)
        query = f"""
        SELECT ?entity ?entityLabel WHERE {{
          VALUES ?entity {{ {values} }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        endpoint.setQuery(query)

        for attempt in range(max_retries):
            try:
                results = endpoint.query().convert()
                for res in results["results"]["bindings"]:
                    uri = res["entity"]["value"]
                    label = res["entityLabel"]["value"]
                    labels[uri] = label
                break  # success
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = base_delay * (2 ** attempt)
                    print(f"⚠️ 429 Too Many Requests. Retrying in {wait}s (attempt {attempt + 1})...")
                    time.sleep(wait)
                else:
                    raise
        else:
            print(f"❌ Failed to fetch labels for batch starting with {batch[0]}")
    return labels

# Fetch labels
print("🔍 Fetching entity labels with backoff...")
entity_labels = fetch_labels(all_entities)
print(f"✅ Fetched {len(entity_labels)} labels")

# Format statements
full_lines = []
subclass_only_lines = []

for _, row in df.iterrows():
    v = entity_labels.get(row["violating_subclass"], row["violating_subclass"])
    e1 = entity_labels.get(row["disjoint_entity1"], row["disjoint_entity1"])
    e2 = entity_labels.get(row["disjoint_entity2"], row["disjoint_entity2"])

    full_line = f"{v} subClassOf {e1}, {v} subClassOf {e2}, {e1} disjointWith {e2}"
    subclass_line = f"{v} subClassOf {e1}, {v} subClassOf {e2}"

    full_lines.append(full_line)
    subclass_only_lines.append(subclass_line)

# Save to plain .txt files (no quotes, no headers)
with open("no_contradictions_full_statements_labels.txt", "w", encoding="utf-8") as f:
    for line in full_lines:
        f.write(line + "\n")

with open("no_contradictions_subclass_only_labels.txt", "w", encoding="utf-8") as f:
    for line in subclass_only_lines:
        f.write(line + "\n")

print("📁 Files written:")
print(" - no_contradictions_full_statements_labels.txt")
print(" - no_contradictions_subclass_only_labels.txt")
