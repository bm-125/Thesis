import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# --- Load ground truth ---
with open('mixed_output_tagged.txt', 'r', encoding='utf-8') as f:
    ground_truth_lines = f.readlines()

ground_truth_labels = [line.strip().split('\t')[-1].strip().lower() for line in ground_truth_lines]

# --- Define model output files ---
model_files = [
    ('Qwen2-7b-Instruct', 'output_qwen2.txt'),
    ('Qwen3-32b', 'output_qwen3.txt'),
    ('DeepSeek-R1', 'output_deepseekd.txt'),
    ('Gemini 2.5 Flash', 'output_gemini_2_5.txt')
]

# --- Compute metrics ---
model_metrics = {}
for model_name, filename in model_files:
    with open(filename, 'r', encoding='utf-8') as f:
        predicted_labels = [line.strip().lower() for line in f.readlines()]

    filtered_y_true = []
    filtered_y_pred = []

    for true_label, pred_label in zip(ground_truth_labels, predicted_labels):
        if pred_label != "unknown":
            filtered_y_true.append(1 if true_label == 'yes' else 0)
            filtered_y_pred.append(1 if pred_label == 'yes' else 0)

    accuracy = accuracy_score(filtered_y_true, filtered_y_pred)
    precision = precision_score(filtered_y_true, filtered_y_pred)
    recall = recall_score(filtered_y_true, filtered_y_pred)
    f1 = f1_score(filtered_y_true, filtered_y_pred)

    model_metrics[model_name] = [accuracy, precision, recall, f1]

# --- Radar plot with curved "web" style ---
labels = ['Accuracy', 'Precision', 'Recall', 'F1']
num_metrics = len(labels)
angles = np.linspace(0, 2*np.pi, num_metrics, endpoint=False).tolist()
angles += angles[:1]  # Close the loop

fig, ax = plt.subplots(figsize=(10,10), subplot_kw=dict(polar=True))

# Add circular gridlines (spider-web style)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
# Set the angular labels
grid_angles = np.degrees(angles[:-1])
ax.set_thetagrids(grid_angles, labels)

# Tweak the 'Precision' label manually after it's created
for label_obj, label_text in zip(ax.get_xticklabels(), labels):
    if label_text == 'Precision':
        label_obj.set_y(label_obj.get_position()[1] - 0.1)  # move it down

ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0], angle=210)
ax.set_ylim(0, 1)

colors = {
    'DeepSeek-R1': 'xkcd:apricot',
    'Qwen2-7b-Instruct': 'xkcd:cherry red',
    'Qwen3-32b': 'xkcd:sky blue',
    'Gemini 2.5 Flash': 'xkcd:sea green'
}

# Plot each model with colormap-assigned color
for idx, (model_name, values) in enumerate(model_metrics.items()):
    values += values[:1]
    color = colors.get(model_name, 'gray')  # Fallback to gray if not found
    ax.plot(angles, values, linewidth=2, label=model_name, color=color)
    ax.fill(angles, values, alpha=0.2, color=color)

plt.legend(loc='best', bbox_to_anchor=(1.2, 1.1))
plt.title("Disjoint Axiom Contradiction Dataset Metrics", size=14)
plt.tight_layout()
plt.show()


