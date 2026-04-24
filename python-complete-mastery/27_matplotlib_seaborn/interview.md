# 📈 Matplotlib and Seaborn — Interview Questions

---

## Beginner

**Q1: What is the difference between Matplotlib's Figure and Axes objects?**

<details>
<summary>💡 Show Answer</summary>

A Figure is the top-level container — the entire canvas or window. An Axes is a single plot inside that Figure — it has its own coordinate system, x and y axes, title, and labels. One Figure can contain multiple Axes objects (a 2×3 grid has 6 Axes). The classic mistake is confusing `axes` (the Axes object) with `axis` (a single x or y axis). When you call `plt.plot()`, Matplotlib implicitly creates a Figure and Axes for you — convenient for quick plots but problematic for multi-plot layouts or reusable code. Best practice: always use `fig, ax = plt.subplots()` to create them explicitly, then call methods on `ax` directly (`ax.plot()`, `ax.set_title()`, etc.).

</details>

<br>

**Q2: What is the difference between `plt.show()` and `plt.savefig()`?**

<details>
<summary>💡 Show Answer</summary>

`plt.show()` renders and displays the plot in an interactive window (or inline in Jupyter) and then clears the current figure. `plt.savefig()` writes the figure to a file without displaying it. The critical rule: if you need both, call `plt.savefig()` before `plt.show()` — otherwise `show()` clears the figure and `savefig()` saves a blank image. Common formats: `.png` (raster, good for web), `.pdf` and `.svg` (vector, good for papers, scale without blurring). Use `dpi=150` or higher for print-quality raster images.

</details>

<br>

**Q3: When would you use Seaborn instead of Matplotlib directly?**

<details>
<summary>💡 Show Answer</summary>

Use Seaborn when you want statistical plots with minimal code: violin plots, pairplots, heatmaps, regression plots. Seaborn handles grouping by categorical variables, draws confidence intervals automatically, and applies polished themes by default. Use Matplotlib directly when you need fine-grained control: custom annotations, non-standard layouts, animations, custom colormaps, or complex multi-panel figures. In practice, most data science workflows use both: Seaborn for fast exploratory plots, Matplotlib for polish and presentation-ready customization.

</details>

<br>

---

## Intermediate

**Q4: How would you plot a confusion matrix for a classification model?**

<details>
<summary>💡 Show Answer</summary>

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns

# Option 1: sklearn built-in
ConfusionMatrixDisplay.from_predictions(y_true, y_pred, display_labels=class_names)

# Option 2: seaborn heatmap (more customizable)
cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted"); plt.ylabel("Actual")
```
The key is `annot=True` to show counts, `fmt="d"` for integer formatting, and a sequential colormap (Blues) since all values are non-negative.

</details>

<br>

**Q5: How do you create a correlation heatmap and what does it tell you?**

<details>
<summary>💡 Show Answer</summary>

```python
corr = df.select_dtypes(include="number").corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True)
```

A correlation heatmap shows pairwise Pearson correlations between all numeric features. Values range -1 to +1. Use a diverging colormap (coolwarm) centered at 0 so the color naturally conveys direction. What it tells you: identify highly correlated features (|r| > 0.9) that may cause multicollinearity in linear models; find features that correlate strongly with the target (useful predictors); spot suspicious correlations that might indicate data leakage.

</details>

<br>

**Q6: How do you visualize the training curve for a neural network?**

<details>
<summary>💡 Show Answer</summary>

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Loss
ax1.plot(history["train_loss"], label="Train")
ax1.plot(history["val_loss"],   label="Validation", linestyle="--")
ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.set_title("Loss Curve")
ax1.legend()

# Accuracy
ax2.plot(history["train_acc"], label="Train")
ax2.plot(history["val_acc"],   label="Validation", linestyle="--")
ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy"); ax2.set_title("Accuracy Curve")
ax2.legend()

plt.tight_layout()
```

You're looking for: training and validation curves converging (good); a large gap where validation degrades but training keeps improving (overfitting); validation better than training (possible test-time augmentation or wrong split).

</details>

<br>

---

## Advanced

**Q7: How would you create a visualization dashboard for ML model evaluation?**

<details>
<summary>💡 Show Answer</summary>

A complete ML evaluation dashboard typically contains: (1) training/validation loss curves (line plot); (2) confusion matrix (heatmap with counts and normalized rates); (3) ROC curve with AUC annotation (`sklearn.metrics.roc_curve`); (4) precision-recall curve; (5) feature importance bar chart; (6) prediction distribution vs actual distribution (overlaid histograms). Lay these out with `plt.subplots(3, 2, figsize=(14, 16))`, use `plt.suptitle()` for the overall title. Save as PDF for reports. Use Streamlit or Dash if the dashboard needs to be interactive.

</details>

<br>

**Q8: How do you create a multi-panel figure with panels of different sizes using GridSpec?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Use `fig.add_gridspec()` to define the grid, then slice it to create panels of different sizes.

```python
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12, 8))
gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.3)

ax_main  = fig.add_subplot(gs[0, :2])   # ← top-left: spans 2 columns
ax_right = fig.add_subplot(gs[0, 2])    # ← top-right: 1 column
ax_bot1  = fig.add_subplot(gs[1, 0])    # ← bottom-left
ax_bot2  = fig.add_subplot(gs[1, 1])    # ← bottom-middle
ax_bot3  = fig.add_subplot(gs[1, 2])    # ← bottom-right
```

Alternatively, `subplot_mosaic` uses letter labels for readable layouts:

```python
fig, axd = plt.subplot_mosaic("AAB\nCCB", figsize=(10, 6))
axd['A'].plot(...)   # ← top-left, 2 units wide
axd['B'].plot(...)   # ← right column, full height
```

**Why it matters:** ML evaluation dashboards commonly need a large main plot (loss curve or confusion matrix) alongside several smaller diagnostic plots.

</details>

<br>

**Q9: What is `tight_layout` and when must you use it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

`plt.tight_layout()` automatically adjusts subplot spacing so axis labels, titles, and tick labels don't overlap each other or the figure edges.

```python
fig, axes = plt.subplots(2, 2)
# ... add plots ...
plt.tight_layout()        # ← call BEFORE savefig, not after
fig.savefig('out.png', bbox_inches='tight')
```

Without it, titles from the bottom row often overlap x-axis labels from the top row. The modern alternative is `layout='constrained'` at figure creation — it handles colorbars and complex layouts better:

```python
fig, axes = plt.subplots(2, 2, layout='constrained')
```

**Why it matters:** The most common cause of ugly saved figures is forgetting `tight_layout` — labels get clipped by the figure boundary.

</details>

<br>

**Q10: How do you add a twin y-axis to show two different metrics on the same plot?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Use `ax.twinx()` to create a second y-axis that shares the same x-axis.

```python
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(epochs, train_loss, 'b-', label='Loss')
ax1.set_ylabel('Loss', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()                               # ← shares x-axis with ax1
ax2.plot(epochs, accuracy, 'r--', label='Accuracy')
ax2.set_ylabel('Accuracy (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Combine legends from both axes:
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')
```

**Why it matters:** Training curves in ML often need loss and accuracy on the same x-axis (epochs) but different y-scales.

</details>

<br>

**Q11: Which colormap should you use for a correlation matrix and why?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Use a **diverging colormap** centered at zero — `'RdBu_r'` or `'coolwarm'` are standard choices.

```python
sns.heatmap(corr_matrix, cmap='RdBu_r',
            vmin=-1, vmax=1,         # ← fix range so center is always 0
            center=0,                # ← Seaborn centers the colormap here
            annot=True, fmt='.2f',
            square=True)
```

Diverging is correct because:
- Values range from -1 (strong negative correlation) to +1 (strong positive)
- Zero is a meaningful midpoint (no correlation)
- The two colors encode direction of correlation

Using a sequential colormap (viridis, Blues) would make -0.9 and 0.0 look similar — misleading.

**Why it matters:** Colormap choice directly affects what patterns a viewer sees. Wrong colormap = wrong story.

</details>

<br>

**Q12: How do you plot an ROC curve in Python?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

```python
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

fpr, tpr, thresholds = roc_curve(y_true, y_scores)  # ← y_scores = probabilities, not labels
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, lw=2, label=f'AUC = {roc_auc:.3f}')
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random (AUC=0.5)')  # ← baseline
ax.set_xlabel('False Positive Rate (1 - Specificity)')
ax.set_ylabel('True Positive Rate (Sensitivity)')
ax.set_title('ROC Curve')
ax.legend(loc='lower right')
```

For imbalanced datasets, prefer the **Precision-Recall curve** (`precision_recall_curve`) — ROC can look optimistic when negatives vastly outnumber positives.

**Why it matters:** ROC/AUC is the standard metric for binary classifiers and appears in almost every ML evaluation.

</details>

<br>

**Q13: How do you plot a training curve and detect overfitting visually?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Plot both train and validation loss on the same axes — the gap between them reveals overfitting.

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.plot(train_loss, label='Train loss')
ax1.plot(val_loss,   label='Val loss', linestyle='--')
ax1.axvline(best_epoch, color='red', linestyle=':', label=f'Best epoch ({best_epoch})')
ax1.set_xlabel('Epoch'); ax1.set_ylabel('Loss')
ax1.set_title('Loss'); ax1.legend()

ax2.plot(train_acc, label='Train acc')
ax2.plot(val_acc,   label='Val acc', linestyle='--')
ax2.set_title('Accuracy'); ax2.legend()

plt.tight_layout()
```

Overfitting signature: train loss keeps falling but val loss starts rising — the divergence point is where early stopping should fire.

**Why it matters:** The learning curve is the first diagnostic every ML engineer looks at. Being able to read and produce it quickly is baseline competency.

</details>

<br>

**Q14: How do you create a feature importance plot?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Sort features by importance and use a horizontal bar chart — horizontal because feature names are long.

```python
import numpy as np, matplotlib.pyplot as plt

importances = model.feature_importances_          # ← from sklearn tree models
feature_names = X.columns.tolist()

sorted_idx = np.argsort(importances)              # ← ascending sort

fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(range(len(sorted_idx)), importances[sorted_idx])
ax.set_yticks(range(len(sorted_idx)))
ax.set_yticklabels(np.array(feature_names)[sorted_idx])
ax.set_xlabel('Importance Score')
ax.set_title('Feature Importance')
plt.tight_layout()
```

For SHAP-based importance, use `shap.summary_plot()` directly — it shows both magnitude and direction of impact.

**Why it matters:** Feature importance plots are the primary tool for model interpretability and feature selection decisions.

</details>

<br>

**Q15: What is the difference between `plt.savefig()` and `fig.savefig()`? What DPI should you use?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

`fig.savefig()` saves a specific figure object. `plt.savefig()` saves the **current active figure** — in scripts with multiple figures open, this can save the wrong one. Prefer `fig.savefig()` for reliability.

```python
fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig('output.png', dpi=150, bbox_inches='tight')  # ← explicit figure
```

DPI guide:
- `72` — screen only (Jupyter display)
- `150` — web/blog (good balance of quality and file size)
- `300` — print and papers (standard requirement)
- `600` — high-resolution printing

`bbox_inches='tight'` prevents labels from being clipped at the figure edge — almost always required.

**Why it matters:** Blurry figures in presentations or papers are caused by wrong DPI. Missing labels are caused by forgetting `bbox_inches='tight'`.

</details>

<br>

**Q16: How do you use `FacetGrid` to compare plots across model groups?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

`FacetGrid` creates a grid of axes where each subplot applies the same plot to a different subset of the data.

```python
import seaborn as sns

g = sns.FacetGrid(results_df, col='model', row='dataset',
                  height=3, aspect=1.2, sharey=True)
g.map(sns.histplot, 'accuracy', bins=20, kde=True)
g.add_legend()
g.set_axis_labels('Accuracy', 'Count')
g.set_titles(col_template='{col_name}', row_template='{row_name}')
```

Alternative for categorical plots: `sns.catplot()` is a shortcut that uses `FacetGrid` internally:

```python
sns.catplot(data=df, x='model', y='accuracy', col='dataset',
            kind='box', height=4, aspect=0.8)
```

**Why it matters:** Comparing model performance across multiple datasets or conditions is a standard reporting pattern — `FacetGrid` produces clean, consistent multi-panel comparisons in a few lines.

</details>

<br>

---

## 🔁 Navigation

| | |
|---|---|
| 📖 README | [README.md](./README.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../26_statistics_and_probability/theory.md](../26_statistics_and_probability/theory.md) |
| ➡️ Next Module | [../28_eda_workflow/theory.md](../28_eda_workflow/theory.md) |

---

**[🏠 Back to README](../README.md)**
