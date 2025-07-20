from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# Load file1 (ground truth)
with open('mixed_output_cardi_tagged.txt', 'r', encoding='utf-8') as f:
    ground_truth_lines = f.readlines()

# Extract the "yes"/"no" labels from file1
ground_truth_labels = [line.strip().split('\t')[-1].strip().lower() for line in ground_truth_lines]

# Load file2 (model predictions)
with open('output_gemini2_5_flash.txt', 'r', encoding='utf-8') as f:
    predicted_labels = [line.strip().lower() for line in f.readlines()]

# Filter out "unknown" predictions and align ground truth accordingly
filtered_y_true = []
filtered_y_pred = []

for true_label, pred_label in zip(ground_truth_labels, predicted_labels):
    if pred_label != "Unknown":
        filtered_y_true.append(1 if true_label == 'yes' else 0)
        filtered_y_pred.append(1 if pred_label == 'yes' else 0)



cm = confusion_matrix(filtered_y_true, filtered_y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu',xticklabels=['No', 'Yes'],yticklabels=['No', 'Yes'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Gemini 2.5 Flash Cardinality Dataset Confusion Matrix')
plt.show()