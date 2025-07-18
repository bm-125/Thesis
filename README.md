Code to detect contradictions and leverage them to build datasets to test wheter language models can distinguish between two contradictory and non-contradictory pairs of statements. This work was based on two datasets: Wikidata and a Gene Ontology based dataset. The work done on Wikidata is stored in master.

reasoner.py: code that merges the original GO KG (November 2024 version) with PPIs from STRING into a .owl file. 
Positive Annotations are integrated using ObjectProperties whilst negative annotations are integrated using NegativeObjectPropertyAssertions.
Also includes code for direct logical and hierarchically inferred contradiction detection.

The original GO based dataset is stored here:
GO KG + PPIs: https://ulisboa-my.sharepoint.com/personal/fc49378_alunos_fc_ul_pt/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Ffc49378%5Falunos%5Ffc%5Ful%5Fpt%2FDocuments%2FPhD%20Project%2Fdata%5FKG%5FPPI&ga=1

