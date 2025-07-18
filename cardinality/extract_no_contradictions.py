from SPARQLWrapper import SPARQLWrapper, JSON
import time

# Load properties from file
def load_properties(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip().split('\t')[0] for line in f if line.strip()]

# Fetch two statements for a given property
def fetch_two_statements_for_property(prop_id):
    print(f"🔍 Querying property {prop_id}...")

    query = f"""
    SELECT DISTINCT ?subjectLabel ?object1Label ?object2Label WHERE {{
      ?subject wdt:{prop_id} ?object1, ?object2.
      FILTER(?object1 != ?object2)

      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    LIMIT 10
    """

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    sparql.addCustomHttpHeader("User-Agent", "MultiValueFetcher/1.0")

    try:
        results = sparql.query().convert()
        output_lines = []
        for result in results["results"]["bindings"]:
            subj = result["subjectLabel"]["value"]
            obj1 = result["object1Label"]["value"]
            obj2 = result["object2Label"]["value"]
            output_lines.append(f"{subj} {prop_id} {obj1}, {subj} {prop_id} {obj2}")
        return output_lines
    except Exception as e:
        print(f"❌ Error with {prop_id}: {e}")
        return []

# Main function
def query_all_properties(input_file="filtered_no_svc.txt", output_file="property_examples.txt"):
    properties = load_properties(input_file)
    print(f"📋 Loaded {len(properties)} properties.")

    with open(output_file, "w", encoding="utf-8") as out:
        for prop in properties:
            lines = fetch_two_statements_for_property(prop)
            for line in lines:
                out.write(line + "\n")
            time.sleep(0.5)  # Be kind to Wikidata

    print(f"✅ Done. Results written to {output_file}")

# Run
if __name__ == "__main__":
    query_all_properties()
