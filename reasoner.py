import rdflib
from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import pandas as pd
from collections import defaultdict

# Load the existing OWL file (GO terms ontology)
existing_owl_file = "go.owl"
g = Graph()
g.parse(existing_owl_file, format="xml")

direct_contradictions = 0
hierarchical_contradictions = 0

# Define namespaces
EX = Namespace("http://example.org#")
GO = Namespace("http://purl.obolibrary.org/obo/")

g.bind("ex", EX)
g.bind("go", GO)
g.bind("rdfs", RDFS)
g.bind("owl", OWL)

# Define Object Properties
HAS_GO_ANNOTATION = URIRef(EX + "has_annotation")
INTERACTS_WITH = URIRef(EX + "interacts_with")

g.add((HAS_GO_ANNOTATION, RDF.type, OWL.ObjectProperty))
g.add((INTERACTS_WITH, RDF.type, OWL.ObjectProperty))

# Define Protein Class
PROTEIN_CLASS = URIRef(GO + "Protein")
g.add((PROTEIN_CLASS, RDF.type, OWL.Class))

# Read CSV files
neg_annots = pd.read_csv('negative_annotations.csv')
pos_annots = pd.read_csv('positive_annotations.csv')
ppis = pd.read_csv('PPIs.csv')

proteins = set()

def to_uri(value):
    """Convert GO terms or other values to proper URIs."""
    value = value.strip()
    if value.startswith("GO:"):
        return URIRef(GO + value.replace(":", "_"))  # Ensure proper URI format
    elif value.startswith("GO_"):
        return URIRef(GO + value)  # Already in correct format
    else:
        return URIRef(EX + value)  # Custom protein or other identifier

# Compute transitive closure for subclass relationships
def compute_transitive_closure(graph):
    subclass_map = defaultdict(set)
    
    # Direct subclass relationships
    for subclass, _, superclass in graph.triples((None, RDFS.subClassOf, None)):
        subclass_map[superclass].add(subclass)
    
    # Equivalent classes
    for class1, _, class2 in graph.triples((None, OWL.equivalentClass, None)):
        subclass_map[class1].add(class2)
        subclass_map[class2].add(class1)
    
    # Compute transitive closure
    def dfs(node, visited):
        if node in visited:
            return
        visited.add(node)
        for child in subclass_map[node]:
            dfs(child, visited)
    
    transitive_closure = defaultdict(set)
    for node in list(subclass_map.keys()):
        visited = set()
        dfs(node, visited)
        transitive_closure[node] = visited
    
    return transitive_closure

subclass_map = compute_transitive_closure(g)

def extract_name(uri):
    return uri.split("/")[-1]  # Extracts the last part of the URI

# Store positive annotations
positive_annotations = defaultdict(set)
for _, row in pos_annots.iterrows():
    protein = to_uri(row[0])
    go_term = to_uri(row[1])
    g.add((protein, RDF.type, PROTEIN_CLASS))
    proteins.add(protein)
    positive_annotations[protein].add(go_term)
    g.add((protein, HAS_GO_ANNOTATION, go_term))

direct_conflict_list = []
hierarchical_conflict_list = []

direct_conflict_set = set()  # To track direct conflicts and prevent hierarchical ones being counted

# Process negative annotations and check for contradictions
for _, row in neg_annots.iterrows():
    protein = to_uri(row[0])
    go_term = to_uri(row[1])
    g.add((protein, RDF.type, PROTEIN_CLASS))
    proteins.add(protein)
    
    # Direct contradictions
    if go_term in positive_annotations.get(protein, set()):
        direct_contradictions += 1
        conflict_entry = (extract_name(protein), extract_name(go_term))
        direct_conflict_list.append(conflict_entry)
        direct_conflict_set.add(conflict_entry)  # Store to prevent duplicate as hierarchical
    
    # Hierarchical contradictions
    for pos_go_term in positive_annotations.get(protein, set()):
        if (extract_name(protein), extract_name(pos_go_term)) not in direct_conflict_set:  # Ensure it's not a direct conflict
            if pos_go_term in subclass_map.get(go_term, set()):  # Positive term is a subclass of the negative term
                hierarchical_contradictions += 1
                hierarchical_conflict_list.append((extract_name(protein), extract_name(pos_go_term), extract_name(go_term)))
    
    # Add NegativePropertyAssertion
    blank_node = BNode()
    g.add((blank_node, RDF.type, OWL.NegativePropertyAssertion))
    g.add((blank_node, OWL.sourceIndividual, protein))
    g.add((blank_node, OWL.assertionProperty, HAS_GO_ANNOTATION))
    g.add((blank_node, OWL.targetIndividual, go_term))

# Process PPIs
for _, row in ppis.iterrows():
    protein1 = to_uri(row[0])
    protein2 = to_uri(row[1])
    g.add((protein1, RDF.type, PROTEIN_CLASS))
    g.add((protein2, RDF.type, PROTEIN_CLASS))
    proteins.update([protein1, protein2])
    g.add((protein1, INTERACTS_WITH, protein2))

print("Direct contradictions:", direct_contradictions)
print("Hierarchical contradictions:", hierarchical_contradictions)
print(len(proteins))
# Save hierarchical contradictions to CSV
hierarchical_conflicts_df = pd.DataFrame(hierarchical_conflict_list, columns=["Protein", "Positive_GO_Term", "Negative_GO_Term"])
hierarchical_conflicts_df.to_csv("hierarchical_contradictions.csv", index=False)
print("✅ Hierarchical contradictions saved to hierarchical_contradictions.csv")

# Save updated OWL file
output_file = "go_kg_updated.owl"
g.serialize(output_file, format="xml")
print(f"✅ OWL file saved as {output_file}")
