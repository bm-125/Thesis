import pandas as pd
import requests
import time
import random

def load_disjoint_contradictions(csv_path):
    df = pd.read_csv(csv_path)
    return df[["disjoint_entity1", "disjoint_entity2", "violating_subclass"]].dropna()

def load_disjoint_class_map(csv_path):
    df = pd.read_csv(csv_path)
    class_map = {}
    for _, row in df.iterrows():
        entity1 = row["entity1"]
        entity2 = row["entity2"]
        cls = row["class"]
        class_map[(entity1, entity2)] = cls
        class_map[(entity2, entity1)] = cls  # allow lookup in either direction
    return class_map

def get_single_subclassof_uri(entity_uri):
    qid = entity_uri.split("/")[-1]
    query = f"""
    SELECT ?superclass WHERE {{
      wd:{qid} wdt:P279 ?superclass .
    }}
    LIMIT 1
    """
    url = 'https://query.wikidata.org/sparql'
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "SubclassBot/1.0 (your_email@example.com)"
    }
    response = requests.get(url, params={'query': query}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        bindings = data['results']['bindings']
        if bindings:
            return bindings[0]['superclass']['value']
    else:
        print(f"Error fetching superclass for {entity_uri}: {response.status_code}")
    return None

def generate_valid_subclass_pairs(contradictions_csv, disjoint_class_csv, output_csv):
    contradiction_rows = load_disjoint_contradictions(contradictions_csv)
    disjoint_class_map = load_disjoint_class_map(disjoint_class_csv)

    results = []
    no_superclass_entities = []

    for _, row in contradiction_rows.iterrows():
        entity1 = row["disjoint_entity1"]
        entity2 = row["disjoint_entity2"]
        violating_subclass = row["violating_subclass"]

        superclass = get_single_subclassof_uri(violating_subclass)

        if not superclass:
            print(f"No superclass found for {violating_subclass}")
            no_superclass_entities.append(violating_subclass)
            continue

        disjoint_class = disjoint_class_map.get((entity1, entity2))
        if disjoint_class and superclass == disjoint_class:
            print(f"Skipping {violating_subclass}: superclass {superclass} matches disjoint class")
            no_superclass_entities.append(violating_subclass)
            continue

        disjoint_entity2 = random.choice([entity1, entity2])

        results.append({
            "disjoint_entity1": superclass,
            "disjoint_entity2": disjoint_entity2,
            "violating_subclass": violating_subclass
        })

        time.sleep(0.5)  # polite to Wikidata

    # Save results
    if results:
        df_out = pd.DataFrame(results)
        df_out.to_csv(output_csv, index=False)
        print(f"Saved {len(df_out)} valid subclass relations to: {output_csv}")
    else:
        print("No valid subclass relations found.")

    # Save skipped entities
    if no_superclass_entities:
        with open("no_superclass_entities.txt", "w") as f:
            for uri in no_superclass_entities:
                f.write(uri + "\n")
        print(f"Logged {len(no_superclass_entities)} skipped entities to: no_superclass_entities.txt")

if __name__ == "__main__":
    generate_valid_subclass_pairs(
        "disjoint_contradictions.csv",
        "disjoint_pairs.csv",
        "valid_subclass_pairs.csv"
    )

