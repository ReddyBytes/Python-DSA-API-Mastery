# 📈 Matplotlib and Seaborn — Interview Questions

---

## Beginner

**Q: What is the difference between Matplotlib's Figure and Axes objects?**

A Figure is the top-level container — the entire canvas or window. An Axes is a single plot inside that Figure — it has its own coordinate system, x and y axes, title, and labels. One Figure can contain multiple Axes objects (a 2×3 grid has 6 Axes). The classic mistake is confusing `axes` (the Axes object) with `axis` (a single x or y axis). When you call `plt.plot()`, Matplotlib implicitly creates a Figure and Axes for you — convenient for quick plots but problematic for multi-plot layouts or reusable code. Best practice: always use `fig, ax = plt.subplots()` to create them explicitly, then call methods on `ax` directly (`ax.plot()`, `ax.set_title()`, etc.).

---

**Q: What is the difference between `plt.show()` and `plt.savefig()`?**

`plt.show()` renders and displays the plot in an interactive window (or inline in Jupyter) and then clears the current figure. `plt.savefig()` writes the figure to a file without displaying it. The critical rule: if you need both, call `plt.savefig()` before `plt.show()` — otherwise `show()` clears the figure and `savefig()` saves a blank image. Common formats: `.png` (raster, good for web), `.pdf` and `.svg` (vector, good for papers, scale without blurring). Use `dpi=150` or higher for print-quality raster images.

---

**Q: When would you use Seaborn instead of Matplotlib directly?**

Use Seaborn when you want statistical plots with minimal code: violin plots, pairplots, heatmaps, regression plots. Seaborn handles grouping by categorical variables, draws confidence intervals automatically, and applies polished themes by default. Use Matplotlib directly when you need fine-grained control: custom annotations, non-standard layouts, animations, custom colormaps, or complex multi-panel figures. In practice, most data science workflows use both: Seaborn for fast exploratory plots, Matplotlib for polish and presentation-ready customization.

---

## Intermediate

**Q: How would you plot a confusion matrix for a classification model?**

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

---

**Q: How do you create a correlation heatmap and what does it tell you?**

```python
corr = df.select_dtypes(include="number").corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True)
```

A correlation heatmap shows pairwise Pearson correlations between all numeric features. Values range -1 to +1. Use a diverging colormap (coolwarm) centered at 0 so the color naturally conveys direction. What it tells you: identify highly correlated features (|r| > 0.9) that may cause multicollinearity in linear models; find features that correlate strongly with the target (useful predictors); spot suspicious correlations that might indicate data leakage.

---

**Q: How do you visualize the training curve for a neural network?**

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

---

## Advanced

**Q: How would you create a visualization dashboard for ML model evaluation?**

A complete ML evaluation dashboard typically contains: (1) training/validation loss curves (line plot); (2) confusion matrix (heatmap with counts and normalized rates); (3) ROC curve with AUC annotation (`sklearn.metrics.roc_curve`); (4) precision-recall curve; (5) feature importance bar chart; (6) prediction distribution vs actual distribution (overlaid histograms). Lay these out with `plt.subplots(3, 2, figsize=(14, 16))`, use `plt.suptitle()` for the overall title. Save as PDF for reports. Use Streamlit or Dash if the dashboard needs to be interactive.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../26_statistics_and_probability/theory.md](../26_statistics_and_probability/theory.md) |
| ➡️ Next Module | [../28_eda_workflow/theory.md](../28_eda_workflow/theory.md) |

---

**[🏠 Back to README](../README.md)**
