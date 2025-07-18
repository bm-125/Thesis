Finding the disjoint contradictions is based on the Disjointness Violations in Wikidata paper. All files access in 23 and 24 of june 2025.
Files:
1. disjoint_subclasses.py: uses the Wikidata SPARQL endpoint to retrieve the subclasses that are pairwise disjoint (determined from the "disjoint union of" property) using the query in the paper and stores the disjoint pairs and the original class in a disjoint_pairs.csv file. The code finds 7209 disjoint pairs. (ir buscar o valor antes das labels)

2. disjoint_contradictions.py: also uses the Wikidata SPARQL endpoint to find subclasses that are subclasses of both members of a disjoint pair, thus finding disjoint axiom contradictions stored in the disjoint_contradictions.csv. The code, as of june 2025, finds 2701 contradictions with no labels.

3. wikidata_disjoint.py and wiki_clean.py: The first code reads the disjoint_contradictions.csv file and replaces the Wikidata identifiers with their english labels. Each contradiction is saved in two different txt files, one that only contains the subclassOf statements (e.g. kaon subClassOf hadron, kaon subClassOf elementary particle) and one containing the full contradiction (e.g. kaon subClassOf hadron, kaon subClassOf elementary particle, hadron disjointWith elementary particle) verificar que a sublasse não é a classe original da disjoint union of
If any of the entities do not have an english label, the row is removed in the second code, resulting in the two final files: contradictions_full_statements_labels.txt and contradictions_subclass_only_labels.txt. This narrows down the total contradictions in this files to 2430. 

4. correct_subclasses.py: Accesses the Wikidata Endpoint and retrieves a "correct" subclassOf relation for each one of the subjects present in the contradictions found before. If it does not find one for a given subject, it skips it. To match the structure of the contradicitons, it also chooses (at random) one of the contradiction subclassof relations to save alongside the entity and the "correct" subclassof relation. This results in 2699 correct ones. The "correct" pairs are then also run through wikidata_disjoint.py and wiki_clean.py so that no entities without labels are stored, which narrows the file down to 2428. The entities that do not have superclasses or that do not have labels are stored in a no_superclass_entities.txt file are also removed manually from the contradiction files. Result: ? valid entities (with both types of subclassof statement pairs).

5. combined.py: Joins the obtained contradiction subclassof pairs with the "correct" ones for a more balanced dataset.50/50 type split. Two files are created: mixed_output.txt contains only the subclassOf pairs and mixed_output_tagged.txt has the correct answer at the end, with a yes or no (whether or not the subclassOf pair is a contradiction or not).

6. disjoint_wiki_prompt_copy.py (also disjoint_wiki_prompt.py is the same but for API usage): Accesses the in-memory model loaded into the servers (qwen2-7b-instruct, DeepSeek-R1-Distill-Qwen-32B and qwen 3 32b), uses the following prompt ("You are a binary classification tool that receives two statements from Wikidata and classifies whether they are contradictory or not. Only answer yes or no. Do not repeat the statements.\n") and the mixed_output.txt file to ask the model whether the pair of statements is contradictory or not. Results are stored in a results_modelname.csv file. (remover os unknowns das stats)

7. response_extraction.py: Cleans the model outputs (removing rogue spaces and dots) and stores the clean answer in output.txt. If the model fails to give an answer, we consider the response to be unknown and it is stored as such.

8. stats.py: Evaluates the model's responses by comparing them to the ground truth stored in mixed_output_tagged.txt. It calculates accuracy, precision, recall, f1 score and a confusion matrix using in-built scikit-learn package. Final results stored in results_modelname.txt.

(ir buscar o valor antes das labels)
(only look for an extra subclass of statement and join it with the contradictory subclassof ones)
(remover os unknowns das stats)
Calcular preço com GPT-4.1 mini (input and output tokens)
Cerebras for qwen 3 32b + o deepseek que já esta instalado e o qwen 2 7b instruct
procurar por predicados que são maioritariamente one to one, encontrar un exemplo pra cada, os negativos são predicatos que não têm de ser one to one. 


