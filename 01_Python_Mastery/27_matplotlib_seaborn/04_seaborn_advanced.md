# 🎯 Seaborn Advanced — FacetGrid, PairGrid, and Statistical Plots

When you have data split across multiple groups — different models, different user segments, different experimental conditions — you want to see the same plot repeated for each group, side by side. Seaborn's `FacetGrid` is the factory for that pattern: you describe the plot once, and Seaborn stamps it out across every group automatically. It is the difference between writing a loop to create 12 plots and writing 3 lines of configuration.

---

## `FacetGrid` — The Same Plot Across Groups

**`FacetGrid`** is a grid of axes where each cell shows the same type of plot filtered to a different subset of the data. You define the layout with `col=` (columns) and `row=` (rows), then call `.map()` to tell Seaborn which plot function to apply and which column to plot.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# --- grid of histograms: one column per model, one row per dataset ---
g = sns.FacetGrid(df, col='model', row='dataset', height=4, aspect=1.2)
# ← height controls the height of each subplot in inches
# ← aspect = width / height ratio of each subplot

g.map(sns.histplot, 'accuracy', bins=20)   # ← 'accuracy' is the column to plot
g.add_legend()
g.set_axis_labels('Accuracy', 'Count')     # ← sets x/y labels across all subplots
g.set_titles(col_template='{col_name}', row_template='{row_name}')
plt.show()
```

For finer control, use `.map_dataframe()` when the plotting function needs the full DataFrame rather than just a column:

```python
g = sns.FacetGrid(df, col='split', hue='class', height=4)
g.map_dataframe(sns.scatterplot, x='feature_1', y='feature_2', alpha=0.5)
g.add_legend()
```

When to use: any time you catch yourself writing a loop over groups to produce the same plot — `FacetGrid` replaces that loop with a declarative grid definition.

---

## `catplot` — The High-Level Categorical Interface

**`catplot`** is Seaborn's recommended entry point for multi-group categorical plots. It wraps `FacetGrid` internally so you can specify `col=`, `row=`, and `hue=` in a single call, without manually building a grid.

```python
# --- box plot per model, split by dataset ---
sns.catplot(
    data=df,
    x='model', y='accuracy',
    kind='box',          # ← 'box' | 'violin' | 'bar' | 'strip' | 'swarm' | 'point'
    col='dataset',       # ← one subplot per dataset
    hue='split',         # ← color by train/val/test
    order=['ModelA', 'ModelB', 'ModelC'],   # ← explicit x-axis ordering
    height=5, aspect=0.8
)
plt.show()

# --- violin plot: shows full distribution shape ---
sns.catplot(data=df, x='class', y='score', kind='violin',
            inner='quartile',   # ← show quartile lines inside violin
            hue='augmented', split=True)   # ← split violin by hue
```

`kind='strip'` overlays individual points; `kind='swarm'` does the same but avoids overlap by spreading points. For dense datasets, `violin` or `box` avoids overplotting.

---

## `PairGrid` and `pairplot`

When exploring a dataset before modeling, you want to see every variable plotted against every other variable — a **scatter matrix**. `pairplot` is the fast path; `PairGrid` gives full control over what appears on the diagonal versus off-diagonal cells.

```python
# --- pairplot: one-liner for scatter matrix ---
sns.pairplot(
    df,
    hue='class',           # ← color points by class label
    diag_kind='kde',       # ← kernel density on the diagonal (vs 'hist')
    plot_kws={'alpha': 0.5},   # ← pass kwargs to the off-diagonal plots
    corner=True            # ← show lower triangle only (less redundancy)
)
plt.suptitle('Feature Pair Plot — Classification EDA', y=1.02)
plt.show()

# --- PairGrid: custom functions per region ---
g = sns.PairGrid(df, vars=['feature1', 'feature2', 'feature3'])
g.map_diag(sns.histplot, kde=True)          # ← diagonal: histogram + KDE
g.map_lower(sns.scatterplot, alpha=0.4)     # ← lower triangle: scatter
g.map_upper(sns.kdeplot, fill=True)         # ← upper triangle: 2D KDE contours
```

For large datasets, `pairplot` becomes slow. A practical strategy: subsample to ~2000 rows before calling `pairplot`, or reduce to the 5-6 most important features identified by feature importance scores.

---

## `lmplot` and `regplot` — Regression Lines

Scatter plots show relationships; **regression plots** add the statistical story on top. `regplot` is the single-axes version; `lmplot` wraps it in a `FacetGrid` for multi-group comparison.

```python
# --- lmplot: regression line per group, across multiple subplots ---
sns.lmplot(
    data=df,
    x='feature', y='target',
    hue='split',       # ← separate regression line per train/val/test
    col='model',       # ← one subplot per model
    ci=95,             # ← shade the 95% confidence interval around the fit line
    scatter_kws={'alpha': 0.3, 's': 20},
    line_kws={'linewidth': 2}
)

# --- regplot: single axes, more control ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.regplot(
    x='x', y='y', data=df,
    scatter_kws={'alpha': 0.3},   # ← semi-transparent points for dense data
    line_kws={'color': 'red'},
    ax=axes[0]
)
axes[0].set_title('Regression fit')

# --- residplot: diagnostic plot for model quality ---
sns.residplot(
    x='x', y='y', data=df,   # ← plots y - predicted_y vs x
    scatter_kws={'alpha': 0.4},
    ax=axes[1]
)
axes[1].axhline(0, color='red', linestyle='--')   # ← horizontal zero line
axes[1].set_title('Residuals — random scatter means good fit')

plt.tight_layout()
plt.show()
```

A good residual plot looks like random scatter around zero. Visible patterns (funnel shape, curve) indicate the model is missing structure in the data.

---

## `clustermap` — Hierarchically Clustered Heatmap

A standard heatmap shows rows and columns in their original order. A **`clustermap`** reorders rows and columns so that similar items appear adjacent, using **hierarchical clustering**. This reveals structure that a fixed-order heatmap hides.

```python
import seaborn as sns
import pandas as pd

# --- clustered correlation heatmap ---
corr_matrix = df.corr()

g = sns.clustermap(
    corr_matrix,
    cmap='coolwarm',       # ← diverging colormap: red = positive, blue = negative
    center=0,              # ← white at zero
    figsize=(10, 10),
    annot=False,           # ← set True to print values (slow for large matrices)
    row_cluster=True,      # ← reorder rows by clustering
    col_cluster=True,      # ← reorder columns by clustering
    method='average',      # ← linkage method: 'average' | 'complete' | 'ward'
    metric='euclidean'     # ← distance metric for clustering
)
g.fig.suptitle('Clustered Feature Correlations', y=1.02)
plt.show()
```

When to use: feature correlation analysis where you want to identify groups of correlated features automatically — the dendrogram on the axes shows which features cluster together, making redundancy and feature groups visible at a glance.

To suppress the dendrogram and only use the reordering:

```python
g = sns.clustermap(corr_matrix, cmap='coolwarm', center=0,
                   row_cluster=True, col_cluster=True,
                   dendrogram_ratio=0.1)   # ← shrink dendrogram to 10% of plot width
```

---

## Seaborn Themes and Context

Seaborn controls two independent things: **style** (background, grid, spines) and **context** (scale of fonts and line widths for the output medium).

```python
import seaborn as sns
import matplotlib.pyplot as plt

# --- set_theme: style + palette + font scale in one call ---
sns.set_theme(
    style='whitegrid',     # ← 'darkgrid' | 'whitegrid' | 'dark' | 'white' | 'ticks'
    palette='muted',       # ← named palette or list of colors
    font_scale=1.2         # ← scale all text elements by 1.2x
)

# --- context: scale everything for the output medium ---
# 'paper' → small, tight (journal figures)
# 'notebook' → default (Jupyter)
# 'talk' → larger text (slides)
# 'poster' → largest (poster presentations)

sns.set_context('talk')   # ← applies globally

# --- context manager: override context for one plot only ---
with sns.plotting_context('talk'):
    fig, ax = plt.subplots()
    sns.histplot(data=df, x='value', hue='class', ax=ax)
    ax.set_title('Distribution by Class')
    plt.show()
# ← context resets after the with block

# --- restore defaults ---
sns.reset_defaults()
```

A practical workflow: develop in `'notebook'` context, then wrap the final export in `with sns.plotting_context('talk')` when preparing slides — all font sizes and line widths scale up automatically without touching any other plot parameters.

---

## Real ML Use Case: `pairplot` for Classification EDA

Before training a classifier, you want to know: are the classes visually separable in any feature pair? Which features might be most discriminative? A `pairplot` colored by class answers both questions in a single plot.

```python
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

# --- load a classification dataset ---
iris = load_iris(as_frame=True)
df = iris.frame
df['species'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

# --- pairplot: scatter matrix colored by class ---
sns.set_theme(style='ticks', font_scale=1.1)

g = sns.pairplot(
    df.drop(columns=['target']),
    hue='species',              # ← color by class label
    diag_kind='kde',            # ← per-class KDE on the diagonal
    plot_kws={'alpha': 0.6, 's': 30},
    diag_kws={'fill': True},    # ← filled KDE curves
    corner=True                 # ← lower triangle only
)

g.fig.suptitle('Iris Dataset — Pairwise Feature Distributions by Class', y=1.02)
g.add_legend(title='Species', bbox_to_anchor=(0.85, 0.7))
plt.show()
```

What to look for: diagonal KDE curves that barely overlap (e.g., setosa vs the others on petal length) identify the most discriminative features. Off-diagonal cells where classes form clean clusters suggest a linear classifier will do well on that feature pair. Overlapping clusters flag where the classifier will struggle.

---

## Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [03_color_and_colormaps.md](./03_color_and_colormaps.md) |
| ➡️ Next Topic | [05_ml_visualization.md](./05_ml_visualization.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
