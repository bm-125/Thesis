from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, f1_score

# Load file1 (ground truth)
with open('mixed_output_tagged.txt', 'r', encoding='utf-8') as f:
    ground_truth_lines = f.readlines()

# Extract the "yes"/"no" labels from file1
ground_truth_labels = [line.strip().split('\t')[-1].strip().lower() for line in ground_truth_lines]

# Load file2 (model predictions)
with open('output_deepseekd.txt', 'r', encoding='utf-8') as f:
    predicted_labels = [line.strip().lower() for line in f.readlines()]

# Filter out "unknown" predictions and align ground truth accordingly
filtered_y_true = []
filtered_y_pred = []

for true_label, pred_label in zip(ground_truth_labels, predicted_labels):
    if pred_label != "Unknown":
        filtered_y_true.append(1 if true_label == 'yes' else 0)
        filtered_y_pred.append(1 if pred_label == 'yes' else 0)

# Compute metrics only on filtered data
accuracy = accuracy_score(filtered_y_true, filtered_y_pred)
precision = precision_score(filtered_y_true, filtered_y_pred)
recall = recall_score(filtered_y_true, filtered_y_pred)
f1 = f1_score(filtered_y_true, filtered_y_pred)
conf_matrix = confusion_matrix(filtered_y_true, filtered_y_pred)

# Print results
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Confusion Matrix:\n", conf_matrix)

