Code to create benchmark datasets with contradictory information based on two datasets: a GO KG enriched with PPIs and the combination of the ConceptNet and Uncommonsense.

reasoner.py: code that merges the original GO KG (November 2024 version) with PPIs from STRING into a .owl file. 
Positive Annotations are integrated using ObjectProperties whilst negative annotations are integrated using NegativeObjectPropertyAssertions.
Also includes code for direct logical and hierarchically inferred contradiction detection.

built_kg.py: Uses the already combined ConceptNet and Uncommonsense datasets to produce a non-flat knowledge graph.
The following relations are considered to imply hierarchical relationships: "FormOf", "HasA", "IsA", "InstanceOf", "HasSubevent", "PartOf"
Whilst these relations are considered to imply disjointness: "Antonym", "DistinctFrom"
The positive and negative triples are processed in the same way as in the GO KG + PPIs dataset.

All original datasets are saved here: CN + UN: https://ulisboa-my.sharepoint.com/personal/fc49378_alunos_fc_ul_pt/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Ffc49378%5Falunos%5Ffc%5Ful%5Fpt%2FDocuments%2FPhD%20Project%2Fdata%5FunCommonsense&ga=1
GO KG + PPIs: https://ulisboa-my.sharepoint.com/personal/fc49378_alunos_fc_ul_pt/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Ffc49378%5Falunos%5Ffc%5Ful%5Fpt%2FDocuments%2FPhD%20Project%2Fdata%5FKG%5FPPI&ga=1
