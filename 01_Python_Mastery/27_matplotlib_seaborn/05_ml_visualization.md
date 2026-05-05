# 🎯 ML Visualization — Plots Every Data Scientist Must Know

Numbers tell you a model has 92% accuracy. Plots tell you whether those 92% are distributed evenly across classes or whether your model is just good at predicting the majority class and failing silently on the minority. A confusion matrix, ROC curve, or learning curve answers questions that accuracy alone cannot. These are the plots that appear in every ML paper, every interview whiteboard, and every production model evaluation report.

---

## Confusion Matrix

Imagine your model is a postal sorter. A confusion matrix shows not just how many letters it delivered correctly, but exactly which destinations got mixed up with which others. Every cell in the grid represents a specific type of error — or a specific type of success. This is the first thing a reviewer looks at when they question a classification result.

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(cmap='Blues')
plt.title('Confusion Matrix')

# Manual version for full control:
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(cm, cmap='Blues')
ax.set_xticks(range(n_classes)); ax.set_xticklabels(class_names, rotation=45)
ax.set_yticks(range(n_classes)); ax.set_yticklabels(class_names)
for i in range(n_classes):
    for j in range(n_classes):
        ax.text(j, i, cm[i, j], ha='center', va='center',
                color='white' if cm[i, j] > cm.max()/2 else 'black')  # ← auto-contrast text
```

The diagonal cells are correct predictions. Off-diagonal cells are misclassifications. **True Positives** sit in the top-left for binary problems. The manual version gives you full control over color contrast, font size, and layout when you need publication-ready output.

---

## ROC Curve and AUC

Think of the ROC curve as a tradeoff dial. At one extreme you catch every positive case but cry wolf constantly. At the other extreme you never false-alarm but miss real cases too. The **ROC curve** (Receiver Operating Characteristic) traces every point along that dial. **AUC** (Area Under the Curve) collapses it to a single number — 0.5 is random, 1.0 is perfect.

```python
from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(y_true, y_scores)
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(fpr, tpr, lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random classifier')  # ← diagonal baseline
ax.set_xlabel('False Positive Rate'); ax.set_ylabel('True Positive Rate')
ax.legend(); ax.set_title('ROC Curve')
```

The dashed diagonal is the random-classifier baseline. Any model worth deploying curves above it. The further the curve bows toward the top-left corner, the better the model is at separating classes.

---

## Precision-Recall Curve

ROC curves look optimistic on **imbalanced datasets** because the large number of true negatives keeps the False Positive Rate artificially low. The **Precision-Recall curve** ignores true negatives entirely — it only asks: of everything we flagged positive, how many were right (precision), and of all actual positives, how many did we find (recall)? This makes it the right tool for fraud detection, medical diagnosis, and any domain where the positive class is rare.

```python
from sklearn.metrics import precision_recall_curve, average_precision_score

precision, recall, _ = precision_recall_curve(y_true, y_scores)
ap = average_precision_score(y_true, y_scores)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(recall, precision, label=f'AP = {ap:.2f}')  # ← AP = area under this curve
ax.set_xlabel('Recall'); ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curve')
ax.legend()
```

**Average Precision (AP)** is the area under this curve — equivalent to AUC but for the precision-recall space. For imbalanced problems, always report AP alongside AUC.

---

## Learning Curves — Training vs Validation Loss

A learning curve is a diagnostic tool. If training loss falls but validation loss climbs, your model is memorizing training data — **overfitting**. If both are high and close together, the model lacks capacity — **underfitting**. The gap between the two curves is your primary signal for deciding whether to add regularization, get more data, or change architecture.

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Loss
ax1.plot(epochs, train_loss, label='Train loss')
ax1.plot(epochs, val_loss, label='Val loss', linestyle='--')
ax1.axvline(best_epoch, color='r', linestyle=':', label='Best epoch')  # ← mark best
ax1.fill_between(epochs, val_loss_lower, val_loss_upper, alpha=0.2)   # ← confidence band
ax1.set_title('Loss'); ax1.legend()

# Accuracy
ax2.plot(epochs, train_acc, label='Train acc')
ax2.plot(epochs, val_acc, label='Val acc', linestyle='--')
ax2.set_title('Accuracy'); ax2.legend()

plt.tight_layout()
```

The vertical red line marking the best epoch tells you exactly where to checkpoint your model. The shaded confidence band (from multiple runs or folds) reveals training stability — wide bands mean the result is sensitive to random seed.

---

## Feature Importance

A bar chart of feature importances answers the question: what does this model actually rely on? Sorted horizontally, it becomes immediately readable — the most important feature sits at the top, the least important at the bottom. This is the first thing a business stakeholder asks for when a model goes to production.

```python
import numpy as np

# Sort by importance for readability
sorted_idx = np.argsort(importances)  # ← ascending, so most important is last (top of barh)
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(range(len(sorted_idx)), importances[sorted_idx], align='center')
ax.set_yticks(range(len(sorted_idx)))
ax.set_yticklabels(np.array(feature_names)[sorted_idx])
ax.set_xlabel('Feature Importance')
ax.set_title('Random Forest Feature Importance')
plt.tight_layout()
```

Always sort. An unsorted feature importance chart is nearly unreadable. For **SHAP values** or permutation importance, the same horizontal bar pattern applies — just swap in the values.

---

## Calibration Plot

A model that outputs 0.8 probability should be right 80% of the time. A **calibration plot** (reliability diagram) checks whether that contract holds. Overconfident models cluster above the diagonal; underconfident models cluster below. This matters in any domain where the probability itself — not just the class label — drives a decision: medicine, finance, risk scoring.

```python
from sklearn.calibration import calibration_curve

fraction_of_positives, mean_predicted_value = calibration_curve(y_true, y_prob, n_bins=10)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(mean_predicted_value, fraction_of_positives, 's-', label='Model')
ax.plot([0, 1], [0, 1], 'k:', label='Perfectly calibrated')  # ← diagonal = perfect
ax.set_xlabel('Mean predicted probability'); ax.set_ylabel('Fraction of positives')
ax.set_title('Calibration Plot (Reliability Diagram)')
ax.legend()
```

The dotted diagonal is the target. **Platt scaling** or **isotonic regression** can post-process a model to bring it closer to the diagonal if calibration is poor.

---

## Decision Boundary

For 2D problems — or any time you reduce a high-dimensional space to two dimensions with PCA or t-SNE — a **decision boundary** plot shows where the model draws the line between classes. This is essential for teaching, debugging, and explaining a classifier's behavior visually.

```python
# Create mesh grid, predict, plot contour
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                     np.linspace(y_min, y_max, 200))
Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

fig, ax = plt.subplots(figsize=(8, 6))
ax.contourf(xx, yy, Z, alpha=0.3, cmap='RdYlBu')   # ← background shows decision regions
ax.scatter(X[:, 0], X[:, 1], c=y, cmap='RdYlBu', edgecolors='black', s=20)
ax.set_title('Decision Boundary')
plt.tight_layout()
```

`contourf` fills regions; `contour` draws lines. The `alpha=0.3` lets the scattered data points show through. Use `cmap='RdYlBu'` for three-class problems and `cmap='RdBu'` for binary ones — the color contrast is more intuitive.

---

## Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [04_seaborn_advanced.md](./04_seaborn_advanced.md) |
| ➡️ Next Topic | [06_saving_and_exporting.md](./06_saving_and_exporting.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
