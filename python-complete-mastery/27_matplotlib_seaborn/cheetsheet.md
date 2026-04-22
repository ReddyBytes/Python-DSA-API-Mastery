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
