# 📈 Matplotlib and Seaborn — Cheatsheet

## Setup

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import numpy as np
import pandas as pd

plt.style.use("seaborn-v0_8-whitegrid")   # or "ggplot", "fivethirtyeight"
sns.set_theme(style="whitegrid", palette="husl", font_scale=1.1)
```

---

## Figure and Axes (Always Use Explicit Form)

```python
# Single plot
fig, ax = plt.subplots(figsize=(8, 5))

# Multiple plots
fig, axes = plt.subplots(2, 3, figsize=(15, 8))   # 2 rows, 3 cols
axes[0, 0].plot(...)                                # access by [row, col]
axes.flatten()                                      # iterate all axes

# Share axes
fig, axes = plt.subplots(1, 2, sharey=True)

# Unequal sizes (GridSpec)
from matplotlib.gridspec import GridSpec
gs = GridSpec(2, 2)
ax1 = fig.add_subplot(gs[0, :])   # top row spans both cols
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])
```

---

## Core Matplotlib Plots

```python
# Line plot
ax.plot(x, y, color="steelblue", linewidth=2, linestyle="--", label="Train", marker="o")

# Scatter plot
ax.scatter(x, y, c=colors, cmap="viridis", s=50, alpha=0.7)

# Bar chart
ax.bar(categories, values, color="steelblue", edgecolor="white", width=0.7)
ax.barh(categories, values)                       # horizontal

# Histogram
ax.hist(data, bins=30, density=True, edgecolor="white")

# Error bars
ax.errorbar(x, y, yerr=error, capsize=4, fmt="o-")

# Fill between (confidence band)
ax.fill_between(x, y_lower, y_upper, alpha=0.3, label="95% CI")

# Horizontal/Vertical lines
ax.axhline(y=0.5, color="red", linestyle=":")
ax.axvline(x=10, color="gray", linestyle="--")

# Imshow (heatmap)
im = ax.imshow(matrix, cmap="Blues", aspect="auto")
plt.colorbar(im, ax=ax)
```

---

## Axes Configuration

```python
ax.set_title("Title", fontsize=14)
ax.set_xlabel("X label", fontsize=12)
ax.set_ylabel("Y label", fontsize=12)
ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)
ax.set_xscale("log")           # log scale
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)
ax.tick_params(axis="x", rotation=45)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["a", "b", "c"])

# Remove spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
```

---

## Save and Show

```python
plt.tight_layout()                              # prevent label clipping
plt.savefig("plot.png", dpi=150, bbox_inches="tight")  # MUST come before show()
plt.savefig("plot.pdf")                         # vector format
plt.show()
plt.close()                                     # release memory
```

---

## Seaborn Distribution Plots

```python
# Histogram + KDE
sns.histplot(df["col"], kde=True, bins=30)
sns.kdeplot(df["col"], fill=True, color="steelblue")

# Box plot
sns.boxplot(x="category", y="value", data=df, hue="group")

# Violin plot (box + distribution)
sns.violinplot(x="category", y="value", data=df, split=True)

# Strip / swarm (individual points)
sns.stripplot(x="category", y="value", data=df, jitter=True)
sns.swarmplot(x="category", y="value", data=df)   # non-overlapping
```

---

## Seaborn Relational Plots

```python
# Scatter with color/size/style encoding
sns.scatterplot(x="x", y="y", hue="category", size="size_var", style="marker_var", data=df)

# Line plot (for time series)
sns.lineplot(x="time", y="value", hue="group", data=df, errorbar="sd")

# Regression scatter
sns.regplot(x="x", y="y", data=df, scatter_kws={"alpha": 0.4})

# Facet grid (one plot per category)
g = sns.FacetGrid(df, col="category", row="group")
g.map(sns.histplot, "value")
```

---

## Seaborn Matrix Plots

```python
# Correlation heatmap
corr = df.select_dtypes("number").corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True)

# Pairplot (all variable combinations)
sns.pairplot(df[["a", "b", "c"]], diag_kind="kde", hue="category")

# Clustermap (heatmap + hierarchical clustering)
sns.clustermap(corr, cmap="coolwarm", figsize=(8, 8))
```

---

## Seaborn Categorical Plots

```python
# Count plot (categorical histogram)
sns.countplot(x="category", hue="group", data=df)

# Bar plot (with error bars)
sns.barplot(x="category", y="value", data=df, errorbar="se")

# Point plot (mean + CI as dots/lines)
sns.pointplot(x="category", y="value", hue="group", data=df)
```

---

## Color Guide

```python
# Named colors
"steelblue", "coral", "forestgreen", "crimson", "gold"

# Seaborn palettes
sns.color_palette("husl", 8)      # 8 distinct, perceptually uniform
sns.color_palette("Blues")         # sequential (light → dark)
sns.color_palette("coolwarm")      # diverging (blue ← 0 → red)
sns.color_palette("colorblind")    # accessible

# Apply globally
sns.set_palette("husl")
```

---

## Golden Rules

1. Always use `fig, ax = plt.subplots()` — explicit form is cleaner and reusable
2. `plt.savefig()` must come before `plt.show()` — `show()` clears the figure
3. Use Seaborn for statistical plots; use Matplotlib directly for custom/complex layouts
4. For presentations: increase `figsize`, `fontsize`, and `linewidth` — defaults are too small
5. Color choice matters: use diverging (coolwarm) for correlations, sequential (Blues) for density

---

## Subplots and Layouts

```python
# Simple grid
fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True)
for ax in axes.flat:   # ← iterate all axes
    ax.plot(x, y)
plt.tight_layout()

# GridSpec — unequal sizes
gs = fig.add_gridspec(2, 3)
ax_main = fig.add_subplot(gs[0, :2])   # ← spans first 2 columns
ax_side = fig.add_subplot(gs[0, 2])

# subplot_mosaic — named panels
fig, axd = plt.subplot_mosaic("AAB\nCCB", figsize=(10, 6))
axd['A'].plot(x, y)     # ← top-left, 2 wide
axd['B'].plot(x, y)     # ← right, full height

# constrained_layout (modern tight_layout replacement)
fig, axes = plt.subplots(2, 2, layout='constrained')
```

---

## Customization

```python
# Global defaults
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 13
plt.rc('axes', labelsize=12, titlesize=14)

# Style sheet
plt.style.use('seaborn-v0_8')
with plt.style.context('dark_background'):   # ← temporary context
    ax.plot(x, y)

# Annotations
ax.annotate('Overfitting starts',
    xy=(15, 0.95), xytext=(20, 0.80),
    arrowprops=dict(arrowstyle='->', color='red'))
ax.axvline(x=15, color='r', linestyle='--', label='Threshold')
ax.fill_between(x, y_lower, y_upper, alpha=0.2, label='CI')

# Twin y-axis
ax2 = ax1.twinx()
ax2.set_ylabel('Accuracy', color='red')
ax2.tick_params(axis='y', labelcolor='red')
```

---

## Color and Colormaps

```python
# Sequential: magnitude data
ax.scatter(x, y, c=values, cmap='viridis', vmin=0, vmax=1)
fig.colorbar(scatter, ax=ax, label='Score')

# Diverging: data with meaningful midpoint (correlations, deltas)
im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1)
fig.colorbar(im, ax=ax)

# Qualitative: categorical data
cmap = plt.cm.get_cmap('tab10', n_classes)   # n distinct colors
colors = [cmap(i) for i in range(n_classes)]

# Accessible palettes (colorblind-safe)
sns.color_palette('colorblind')   # use for categorical
# viridis, plasma, cividis are perceptually uniform — prefer over jet/rainbow
```

---

## Seaborn Advanced

```python
# FacetGrid — same plot per group
g = sns.FacetGrid(df, col='model', row='split', height=3, aspect=1.2)
g.map(sns.histplot, 'accuracy')
g.add_legend()

# catplot — high-level categorical with facets
sns.catplot(data=df, x='model', y='score', col='dataset',
            kind='box', height=4)

# PairGrid / pairplot
sns.pairplot(df, hue='class', diag_kind='kde', plot_kws={'alpha': 0.4})

# Regression
sns.lmplot(data=df, x='feature', y='target', hue='split', ci=95)
sns.residplot(x='feature', y='residuals', data=df)  # ← model diagnostics

# Clustered heatmap
sns.clustermap(corr_df, cmap='coolwarm', center=0, figsize=(10, 10))

# Theme
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.2)
with sns.plotting_context('talk'):   # paper | notebook | talk | poster
    sns.histplot(data=df, x='val')
```

---

## ML Visualization

```python
# Confusion matrix
from sklearn.metrics import ConfusionMatrixDisplay
ConfusionMatrixDisplay.from_predictions(y_true, y_pred, cmap='Blues').plot()

# ROC curve
from sklearn.metrics import roc_curve, auc
fpr, tpr, _ = roc_curve(y_true, y_scores)
ax.plot(fpr, tpr, label=f'AUC={auc(fpr,tpr):.2f}')
ax.plot([0,1],[0,1],'k--')   # ← random baseline

# Learning curves
ax.plot(train_loss, label='Train'); ax.plot(val_loss, '--', label='Val')
ax.axvline(best_epoch, color='r', linestyle=':')

# Feature importance (horizontal bar)
sorted_idx = np.argsort(importances)
ax.barh(np.array(names)[sorted_idx], importances[sorted_idx])

# Decision boundary
xx, yy = np.meshgrid(np.linspace(x1,x2,200), np.linspace(y1,y2,200))
Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
ax.contourf(xx, yy, Z, alpha=0.3, cmap='RdYlBu')
```

---

## Saving Figures

```python
# Always use fig.savefig (not plt.savefig) when you have multiple figs
fig.savefig('plot.png',
    dpi=150,                 # 72=screen | 150=web | 300=paper
    bbox_inches='tight',     # ← prevent label clipping
    transparent=False,
    facecolor='white')

# Format guide:
# PNG  → web, general use (raster)
# SVG  → web (vector, scalable)
# PDF  → LaTeX papers (vector, fonts embedded)
# JPEG → avoid for charts (lossy artifacts)

plt.close(fig)    # ← free memory after saving
plt.close('all')  # ← close all open figures (use in loops)
```
