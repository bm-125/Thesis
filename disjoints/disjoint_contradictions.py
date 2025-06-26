import os
import time
import pandas as pd
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.error

# ---------- CONFIGURATION ----------
INPUT_FILE = "disjoint_pairs.csv"
OUTPUT_FILE = "disjoint_contradictions.csv"
BATCH_SIZE = 20  # how many disjoint pairs to check at once
RETRY_LIMIT = 5
BASE_BACKOFF = 5  # seconds
# -----------------------------------

# Load disjoint pairs
disjoint_df = pd.read_csv(INPUT_FILE)

# Load existing contradictions if resuming
if os.path.exists(OUTPUT_FILE):
    contradictions_df = pd.read_csv(OUTPUT_FILE)
    seen = set(
        (row["disjoint_entity1"], row["disjoint_entity2"], row["violating_subclass"])
        for _, row in contradictions_df.iterrows()
    )
    contradictions = contradictions_df.to_dict(orient="records")
    print(f"Resuming with {len(contradictions)} existing contradiction results.")
else:
    contradictions = []
    seen = set()

# Setup SPARQL
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# Helper: run query with exponential backoff
def query_with_retry(query):
    sparql.setQuery(query)
    for attempt in range(RETRY_LIMIT):
        try:
            return sparql.query().convert()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = BASE_BACKOFF * (2 ** attempt)
                print(f"429 Too Many Requests. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded.")

# Helper: create SPARQL VALUES batch
def make_values_block(pairs):
    block = " ".join(f"( <{e1}> <{e2}> )" for e1, e2 in pairs)
    return f"VALUES (?e1 ?e2) {{ {block} }}"

# Main loop
all_pairs = list(
    {(row["entity1"], row["entity2"]) for _, row in disjoint_df.iterrows()}
)
batches = [all_pairs[i:i + BATCH_SIZE] for i in range(0, len(all_pairs), BATCH_SIZE)]

for batch in tqdm(batches, desc="Processing disjoint batches"):
    values_block = make_values_block(batch)
    query = f"""
    SELECT DISTINCT ?e1 ?e2 ?subclass WHERE {{
      {values_block}
      ?subclass wdt:P279+ ?e1 .
      ?subclass wdt:P279+ ?e2 .
    }}
    """

    try:
        results = query_with_retry(query)
        for result in results["results"]["bindings"]:
            e1 = result["e1"]["value"]
            e2 = result["e2"]["value"]
            subclass = result["subclass"]["value"]

            key = (e1, e2, subclass)
            if key not in seen:
                contradictions.append({
                    "disjoint_entity1": e1,
                    "disjoint_entity2": e2,
                    "violating_subclass": subclass
                })
                seen.add(key)
    except Exception as e:
        print(f"Error processing batch starting with {batch[0]}: {e}")
        continue

    # Save progress
    pd.DataFrame(contradictions).to_csv(OUTPUT_FILE, index=False)

print("✅ Done. Final contradictions saved to:", OUTPUT_FILE)

