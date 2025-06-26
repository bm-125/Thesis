import pandas as pd
import requests
import itertools
import random
import time

WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/"

def load_input(csv_path):
    df = pd.read_csv(csv_path)
    # Extract disjoint pairs (unordered) from URIs
    disjoint_pairs = set(
        tuple(sorted([row["disjoint_entity1"], row["disjoint_entity2"]]))
        for _, row in df.iterrows()
        if pd.notna(row["disjoint_entity1"]) and pd.notna(row["disjoint_entity2"])
    )
    # Unique violating entities (URIs)
    entities = df["violating_subclass"].dropna().unique().tolist()
    return entities, disjoint_pairs

def get_subclassof_uris(entity_uri):
    qid = entity_uri.split("/")[-1]
    query = f"""
    SELECT ?superclass WHERE {{
      wd:{qid} wdt:P279 ?superclass .
    }}
    """
    url = 'https://query.wikidata.org/sparql'
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "SubclassBot/1.0 (your_email@example.com)"
    }
    response = requests.get(url, params={'query': query}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [binding['superclass']['value'] for binding in data['results']['bindings']]
    else:
        print(f"Error fetching subclasses for {qid}: {response.status_code}")
        return []

def generate_unordered_pairs(items):
    return list(itertools.combinations(set(items), 2))

def generate_valid_subclass_pairs(input_csv, output_csv):
    entities, disjoint_pairs = load_input(input_csv)
    results = []

    for entity_uri in entities:
        superclasses = get_subclassof_uris(entity_uri)
        subclass_pairs = generate_unordered_pairs(superclasses)

        valid_pairs = [
            (a, b) for (a, b) in subclass_pairs
            if tuple(sorted((a, b))) not in disjoint_pairs
        ]

        for subclass1, subclass2 in valid_pairs:
            results.append({
                "disjoint_entity1": subclass1,
                "disjoint_entity2": subclass2,
                "violating_subclass": entity_uri
            })

        time.sleep(0.5)  # Be polite to Wikidata

    if results:
        df_out = pd.DataFrame(results)
        df_out.to_csv(output_csv, index=False)
        print(f"Saved {len(df_out)} valid subclass pairs to: {output_csv}")
    else:
        print("No valid subclass pairs found.")
if __name__ == "__main__":
    generate_valid_subclass_pairs("disjoint_contradictions.csv", "valid_subclass_pairs.csv")