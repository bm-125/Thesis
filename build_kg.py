import pandas as pd
from rdflib import Graph, Namespace, RDF, OWL, RDFS, BNode
from urllib.parse import quote
import re

uri_cache = {}

def to_valid_uri(term):
    if pd.isna(term):
        return "unknown"
    term = str(term)
    if term in uri_cache:
        return uri_cache[term]
    
    cleaned_term = re.sub(r'[^a-zA-Z0-9_\-.]', '_', term)
    cleaned_term = quote(cleaned_term)
    
    uri_cache[term] = cleaned_term
    return cleaned_term

def process_row(row, EX):
    count_disjoint=0
    count_hierarchical=0
    subject = to_valid_uri(row.subject)
    predicate = to_valid_uri(row.predicate)
    obj = to_valid_uri(row.object)

    if row.predicate.startswith("dbpedia:"):
        return []

    triples = []

    if row.type == "positive":
        triples.append((EX[subject], EX[predicate], EX[obj]))

        hierarchical_preds = {"FormOf", "HasA", "IsA", "InstanceOf", "HasSubevent", "PartOf"}
        if row.predicate in hierarchical_preds:
            triples.append((EX[subject], RDFS.subClassOf, EX[obj]))
            count_hierarchical += 1

        disjoint_preds = {"Antonym", "DistinctFrom"}
        if row.predicate in disjoint_preds:
            triples.append((EX[subject], OWL.disjointWith, EX[obj]))
            count_disjoint+=1

    elif row.type == "negative":
        blank_node = BNode()
        triples.extend([
            (blank_node, RDF.type, OWL.NegativePropertyAssertion),
            (blank_node, OWL.sourceIndividual, EX[subject]),
            (blank_node, OWL.assertionProperty, EX[predicate]),
            (blank_node, OWL.targetIndividual, EX[obj])
        ])
    
    return triples,count_hierarchical, count_disjoint

def csv_to_owl(input_csv, output_owl, num_lines=None, chunk_size=10000):
    g = Graph()
    EX = Namespace("http://example.org/ontology#")
    g.bind("ex", EX)
    count_total_disjoint=0
    count_total_hierarchical=0
    unique_entities = set()
    unique_relations = set()

    if num_lines is not None:
        df_iter = [pd.read_csv(input_csv, nrows=num_lines)]  # Wrap it in a list
    else:
        df_iter = pd.read_csv(input_csv, chunksize=chunk_size)  # Generator

    for chunk in df_iter:
        unique_entities.update(chunk["subject"].values)
        unique_entities.update(chunk["object"].values)
        unique_relations.update(chunk["predicate"].values)

        for row in chunk.itertuples(index=False):
            triples = process_row(row, EX)[0]
            count_total_disjoint+= process_row(row, EX)[2]
            count_total_hierarchical+= process_row(row, EX)[1]
            for triple in triples:
                g.add(triple)

    for entity in unique_entities:
        g.add((EX[to_valid_uri(entity)], RDF.type, OWL.Class))

    for rel in unique_relations:
        g.add((EX[to_valid_uri(rel)], RDF.type, OWL.ObjectProperty))

    g.serialize(destination=output_owl, format="turtle")
    print(count_total_disjoint,count_total_hierarchical)


if __name__ == '__main__':
    csv_to_owl("merged_dataset.csv", "not_flat_kg.owl", num_lines=None)

