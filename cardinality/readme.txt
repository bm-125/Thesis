Finding the cardinality constrained contradictions in Wikidata was done by finding properties that had the single value constraint (Q19474404) that is used to indicate when a property has a one-to-one cardinality constraint for each subject. 

1. cardinality_search.py: Finds every property with a single value contraint defined in Wikidata (using the Wikidata endpoint and a SPARQL query) and stores them in a file. Saved 8665 properties to single_value_properties.txt.

2. cardinality_clean.py: Analyses the single value constrained predicates and removes any that are numerical identifiers (also supplemented with manual cleaning), results in 451 properties stored in filtered_properties.txt.

3. cardinality_violations.py: Uses a SPARQL query to find every cardinality constrained contradiction for the filtered predicates, meaning that if for the same subject and property there are more than one object, this is a contradiction. Results in 446225 contradictions found in 277 of the filtered predicates.

4. analyse_extract_contradictions.py: Also queries the endpoint to retrieve up to 3 contradictions for each one of the 277 predicates with contradictions. If less than three, the ones that exist are stored in contradictions.csv. Saves ... contradictions in total.

Number of contradictions without labels: 708