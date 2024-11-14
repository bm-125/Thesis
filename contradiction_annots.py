import numpy
import random
import os
import rdflib
from rdflib.namespace import RDF, OWL, RDFS

import networkx as nx

# First: Transforming from rdf to KG (the same as the TrueWalks code)
def _identity(x): return x

def _rdflib_to_networkx_graph(
        graph,
        nxgraph,
        calc_weights,
        edge_attrs,
        transform_s=_identity, transform_o=_identity):
    """Helper method for multidigraph, digraph and graph.
    Modifies nxgraph in-place!
    Arguments:
        graph: an rdflib.Graph.
        nxgraph: a networkx.Graph/DiGraph/MultiDigraph.
        calc_weights: If True adds a 'weight' attribute to each edge according
            to the count of s,p,o triples between s and o, which is meaningful
            for Graph/DiGraph.
        edge_attrs: Callable to construct edge data from s, p, o.
           'triples' attribute is handled specially to be merged.
           'weight' should not be generated if calc_weights==True.
           (see invokers below!)
        transform_s: Callable to transform node generated from s.
        transform_o: Callable to transform node generated from o.
    """
    assert callable(edge_attrs)
    assert callable(transform_s)
    assert callable(transform_o)
    import networkx as nx
    for s, p, o in graph:
        ts, to = transform_s(s), transform_o(o)  # apply possible transformations
        data = nxgraph.get_edge_data(ts, to)
        if data is None or isinstance(nxgraph, nx.MultiDiGraph):
            # no edge yet, set defaults
            data = edge_attrs(s, p, o)
            if calc_weights:
                data['weight'] = 1
            nxgraph.add_edge(ts, to, **data)
        else:
            # already have an edge, just update attributes
            if calc_weights:
                data['weight'] += 1
            if 'triples' in data:
                d = edge_attrs(s, p, o)
                data['triples'].extend(d['triples'])

def process_ontology_children(ontology_file_path):
    g_ontology = rdflib.Graph()
    g_ontology.parse(ontology_file_path, format='xml')
    g = rdflib.Graph()

    GO_terms = []
    for (sub, pred, obj) in g_ontology.triples((None, RDFS.subClassOf, None)):
        if g_ontology.__contains__(
                (sub, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), None)):
            if g_ontology.__contains__(
                    (obj, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), None)):
                g.add((sub, pred, obj))
                if sub not in GO_terms:
                    GO_terms.append(sub)
                if obj not in GO_terms:
                    GO_terms.append(obj)

    G = nx.DiGraph()
    _rdflib_to_networkx_graph(g, G, calc_weights=False, edge_attrs=lambda s, p, o: {})

    dependencies = {}
    for GO_term in GO_terms:
        children = []
        for child in nx.ancestors(G, GO_term):
            children.append(str(child))
        dependencies[str(GO_term)] = children
    print('Ontology children processed.')
    return dependencies


def process_ontology(ontology_file_path):
    g_ontology = rdflib.Graph()
    g_ontology.parse(ontology_file_path, format='xml')
    g = rdflib.Graph()

    GO_terms = []
    for (sub, pred, obj) in g_ontology.triples((None, RDFS.subClassOf, None)):
        if g_ontology.__contains__(
                (sub, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), None)):
            if g_ontology.__contains__(
                    (obj, rdflib.term.URIRef('http://www.geneontology.org/formats/oboInOwl#hasOBONamespace'), None)):
                g.add((sub, pred, obj))
                if sub not in GO_terms:
                    GO_terms.append(sub)
                if obj not in GO_terms:
                    GO_terms.append(obj)

    G = nx.DiGraph()
    _rdflib_to_networkx_graph(g, G, calc_weights=False, edge_attrs=lambda s, p, o: {})
    dependencies_child, dependencies_parent = {}, {}
    # The links were removed to match the annotations file used (that only contains the GO term number)
    for GO_term in GO_terms:
        children, parents = [], []
        for child in nx.ancestors(G, GO_term):
            children.append(str(child).removeprefix('http://purl.obolibrary.org/obo/'))
        for parent in nx.descendants(G, GO_term):
            parents.append(str(parent).removeprefix('http://purl.obolibrary.org/obo/'))
        dependencies_child[str(GO_term)] = children
        dependencies_parent[str(GO_term)] = parents
    print('Ontology has been processed.')

    return dependencies_child, dependencies_parent


def process_annotations_gaf(annotations_file_path):
    import pandas as pd
    data = pd.read_csv(annotations_file_path, sep="\t", skiprows=41, header=None)
    data = data.iloc[:,[1,3,4,6,8]].T.reset_index(drop=True).T
    annotas = data.iloc[:,[0,1,2,4]]
    dic_annotations = {}
    for line in range(1, len(annotas)):
        entity, process, types, functions = annotas[0][line], annotas[1][line], annotas[2][line], annotas[4][line]
    
    # Initialize only if entity is not already in dic_annotations
        if entity not in dic_annotations:
            dic_annotations[entity] = {'pos': [], 'neg': []}

        x = process.startswith("NOT")
        if not x:
            dic_annotations[entity]['pos'].append(types)
            dic_annotations[entity]['pos'].append(functions)
        else:
            dic_annotations[entity]['neg'].append(types)
            dic_annotations[entity]['neg'].append(functions)
    print('Annotations processed.')
    return dic_annotations


def contraditory_annotations(ontology_file_path, annotations_file_path):
    """Counts and categorizes contradictions: direct contradictions (so the same gene has positve and negative annotations) 
    and contradictions related to the hierarchical properties of the ontology (It collects all positive annotations and their parent terms (based on the ontology hierarchy).
It then filters out any negative annotations that contradict these positive annotations. 
Specifically, if a negative annotation is a parent of, or equal to, any positive annotation, they are added to the total number of contradictions.)
    """
    import pandas as pd
    dependencies_children, dependencies_parents = process_ontology(ontology_file_path)
    
    # Initialize counters and lists
    molec_function_contra = 0
    bio_process_contra = 0
    celular_comp_contra = 0
    entities_contradiction_F = []
    entities_contradiction_C = []
    entities_contradiction_P = []
    
    dic_annotations = process_annotations_gaf(annotations_file_path)
    
    # Process each entity to detect contradictions
    for ent in dic_annotations:
        # Gather all positive annotations and their parents for this entity
        parents_positive_annots = set()
        for an in dic_annotations[ent]['pos']:
            parents_positive_annots.add(an)
            if an in dependencies_parents:
                parents_positive_annots.update(dependencies_parents[an])

        # Check each negative annotation for contradictions
        for an in dic_annotations[ent]['neg']:
            if an in parents_positive_annots:
                # Classify the contradiction type based on annotation prefix
                if an.startswith('F'):
                    molec_function_contra += 1
                    entities_contradiction_F.append(ent)
                elif an.startswith('C'):
                    celular_comp_contra += 1
                    entities_contradiction_C.append(ent)
                elif an.startswith('P'):
                    bio_process_contra += 1
                    entities_contradiction_P.append(ent)
    
    
    # Initialize direct contradiction counter and storage
    number_direct_contradictions = 0
    dic_annotations = process_annotations_gaf(annotations_file_path)
    entities_with_contradictions = []

    for ent in dic_annotations:
        # Separate GO terms and their types for positive and negative annotations
        pos_annotations = {dic_annotations[ent]['pos'][i]: dic_annotations[ent]['pos'][i+1]
                           for i in range(0, len(dic_annotations[ent]['pos']), 2)}
        neg_annotations = {dic_annotations[ent]['neg'][i]: dic_annotations[ent]['neg'][i+1]
                           for i in range(0, len(dic_annotations[ent]['neg']), 2)}

        # Find direct contradictions: exact GO terms in both pos and neg
        direct_contradictions = set(pos_annotations.keys()).intersection(set(neg_annotations.keys()))

        # If direct contradictions found, count them and store the entity
        if direct_contradictions:
            number_direct_contradictions += 1
            entities_with_contradictions.append(ent)

    # Summary of contradiction count
    print("Contradictions:")
    print("Total direct contradictions:", number_direct_contradictions)
    print(f"Molecular Function (F): {molec_function_contra}")
    print(f"Cellular Component (C): {celular_comp_contra}")
    print(f"Biological Process (P): {bio_process_contra}")
    print('Total number of contradictions in dataset:','\t',number_direct_contradictions+molec_function_contra+celular_comp_contra+bio_process_contra)
    


    
    #From here on downwards it is the part where I write the useful annotations in a .tsv file.
    new_file_annot = open(new_annotations_file_path, 'w')

    #All the annotations, including contradictions, are saved in the contradiction_annotations.tsv file.
    data = pd.read_csv(annotations_file_path, sep="\t", skiprows=41, header=None)
    data = data.iloc[:,[1,3,4,6,8]].T.reset_index(drop=True).T
    annotas = data.iloc[:,[0,1,2,4]]
    for line in range(1, len(annotas)):
        entity, process, types, functions = annotas[0][line], annotas[1][line], annotas[2][line], annotas[4][line]
        new_file_annot.write(entity+"\t"+process+'\t'+types+'\t'+functions)
        new_file_annot.write('\n')

    new_file_annot.close()
    
    print('Contradictions processed.')



if __name__== '__main__':
    # The files used for this work were extracted from the GO site archive.
    # GO annotations: https://release.geneontology.org/2021-09-01/annotations/index.html
    # GO ontology: https://release.geneontology.org/2021-09-01/ontology/index.html
    # The 2021 version was chosen to mirror the one used in TrueWalks.
    ontology_file_path = "go.owl"
    annotations_gaf_file_path = "goa_human.gaf"
    new_annotations_file_path = "contradiction_annotations.tsv"
    contraditory_annotations(ontology_file_path, annotations_gaf_file_path)
