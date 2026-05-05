# 🎯 Color and Colormaps — Encoding Information in Color

Color in a visualization is not decoration — it carries information. A heatmap where "high" and "low" use colors that look similar to colorblind viewers fails to communicate. A diverging colormap centered at zero tells a completely different story than a sequential colormap starting at zero. Choosing the right colormap for the right data type is a skill that separates clear visualizations from misleading ones.

---

## Types of Colormaps

Every colormap belongs to one of three families, and the choice must match the nature of the data.

**Sequential colormaps** (`viridis`, `plasma`, `Blues`, `YlOrRd`) map a single direction of magnitude — from low to high. Use them when your data has no meaningful midpoint: loss values, pixel intensities, probability scores. `viridis` and `plasma` are the default recommendations because they are perceptually uniform (equal steps in data produce equal perceived steps in color) and print correctly in greyscale.

**Diverging colormaps** (`RdBu`, `coolwarm`, `PiYG`) have a neutral midpoint — usually white or light grey — and diverge in two directions. Use them when the data has a meaningful center: correlation coefficients (center at 0), weight changes (center at 0), temperature anomalies (center at baseline). The viewer immediately reads "above" and "below" as qualitatively different.

**Qualitative colormaps** (`tab10`, `Set2`, `Paired`) assign distinct hues with no implied order. Use them for categorical data: class labels, model names, dataset splits. There is no "higher" or "lower" — just "different".

| Data type | Example | Right colormap family |
|---|---|---|
| Model loss (0 to 1) | Training curve heatmap | Sequential |
| Correlation matrix (-1 to 1) | Feature correlation | Diverging |
| Class labels (A, B, C) | Scatter by species | Qualitative |

---

## Using Colormaps in Plots

The two most common patterns are scatter plots (continuous color per point) and image/heatmap plots.

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# --- scatter with color encoding a continuous variable ---
x = np.random.randn(200)
y = np.random.randn(200)
values = np.random.rand(200)   # ← the variable encoded by color

scatter = axes[0].scatter(x, y, c=values, cmap='viridis', vmin=0, vmax=1)
fig.colorbar(scatter, ax=axes[0], label='Loss')   # ← add colorbar with label
axes[0].set_title('Scatter: sequential colormap')

# --- imshow / heatmap with diverging colormap ---
matrix = np.random.uniform(-1, 1, (8, 8))

im = axes[1].imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1)   # ← _r reverses the colormap
fig.colorbar(im, ax=axes[1], label='Correlation')
axes[1].set_title('Heatmap: diverging colormap')

plt.tight_layout()
plt.show()
```

Key parameters:
- `c=values` — the array whose values map to color
- `cmap='viridis'` — the colormap name (string or `Colormap` object)
- `vmin`, `vmax` — clamp the color range; values outside are clipped to the endpoint colors
- `fig.colorbar(mappable, ax=ax)` — always attach the colorbar to the specific axes it belongs to

---

## `Normalize` — Controlling the Color Range

By default, Matplotlib maps the full data range to the full colormap. **`Normalize`** objects let you override this behavior.

```python
import matplotlib.colors as mcolors

# --- linear normalization with explicit bounds ---
norm = mcolors.Normalize(vmin=0, vmax=100)
scatter = ax.scatter(x, y, c=values, cmap='plasma', norm=norm)

# --- log-scale color (useful for count data spanning orders of magnitude) ---
norm_log = mcolors.LogNorm(vmin=1, vmax=10000)   # ← values must be > 0
im = ax.imshow(count_matrix, cmap='YlOrRd', norm=norm_log)

# --- diverging with asymmetric range (e.g., -0.5 to 0 to 2.0) ---
norm_two = mcolors.TwoSlopeNorm(vmin=-0.5, vcenter=0, vmax=2.0)
# ← midpoint stays white at 0, even though negative range is smaller
im = ax.imshow(matrix, cmap='RdBu_r', norm=norm_two)
```

**`TwoSlopeNorm`** is particularly useful in ML when you want zero to always render as neutral white in a diverging colormap, even when your data is asymmetric (e.g., residuals mostly positive, a few slightly negative).

---

## Discrete Colormaps from Continuous

Sometimes you have a small number of classes and want each class to get a distinct color pulled from a continuous colormap — useful when Matplotlib's default qualitative palettes don't have enough colors.

```python
import matplotlib.pyplot as plt
import matplotlib.cm as cm

n_classes = 5
cmap = plt.cm.get_cmap('viridis', n_classes)   # ← slice colormap into n equal steps

# map integer class labels to colors
for i, class_label in enumerate(range(n_classes)):
    color = cmap(i)   # ← returns (R, G, B, A) tuple
    ax.scatter(x[labels == i], y[labels == i], color=color, label=f'Class {i}')

ax.legend()

# alternative: build a color list directly
colors = [cmap(i) for i in range(n_classes)]
```

For modern Matplotlib (3.7+), prefer `plt.colormaps['viridis'].resampled(n_classes)` over the deprecated `get_cmap`.

---

## Accessible and Colorblind-Friendly Palettes

Roughly 8% of men have some form of color vision deficiency. Choosing inaccessible colormaps means your plots fail for a meaningful fraction of your audience — and in scientific contexts, they can actively mislead.

**Safe choices:**
- `viridis`, `plasma`, `cividis` — perceptually uniform, colorblind-safe, greyscale-friendly. Use for sequential data.
- Seaborn's `color_palette('colorblind')` — 6-color categorical palette designed for accessibility.
- `sns.color_palette('husl', n_colors)` — evenly spaced hues in perceptual space; generates any number of distinct colors.

**Avoid:**
- `jet` — red-green transition is invisible to red-green colorblind viewers; false contours appear at yellow and cyan.
- `rainbow` — same problems as `jet`, non-monotonic lightness means equal data steps look unequal.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# categorical palette: 8 colorblind-safe colors
palette = sns.color_palette('colorblind', n_colors=8)
sns.palplot(palette)   # ← preview the palette as color swatches

# custom n-color palette using perceptual hue space
husl_palette = sns.color_palette('husl', n_colors=12)

# using it in a plot
fig, ax = plt.subplots()
for i, (group_name, group_df) in enumerate(df.groupby('model')):
    ax.plot(group_df['epoch'], group_df['loss'],
            color=husl_palette[i], label=group_name)
ax.legend()
```

---

## Color in Lines and Bars

Beyond colormaps, basic color control applies everywhere.

```python
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# --- hex color and alpha ---
axes[0].plot(x, y, color='#2196F3', linewidth=2, alpha=0.8, label='Train')
# ← alpha controls transparency: 0 = invisible, 1 = opaque
axes[0].plot(x, y2, color='#F44336', linewidth=2, alpha=0.8, label='Val')
axes[0].legend()

# --- named colors ---
axes[1].bar(categories, values,
            color='steelblue',     # ← one of Matplotlib's named colors
            edgecolor='black',     # ← outline color
            linewidth=0.8)

# --- per-bar colors from a list ---
bar_colors = ['#4CAF50' if v > 0 else '#F44336' for v in values]
axes[2].bar(categories, values, color=bar_colors, edgecolor='white', linewidth=0.5)

plt.tight_layout()
plt.show()
```

Common color formats Matplotlib accepts: named strings (`'red'`, `'steelblue'`), hex (`'#2196F3'`), RGB tuple (`(0.13, 0.59, 0.95)`), single float for greyscale (`'0.75'`).

---

## Real ML Use Case: Correlation Heatmap for Feature Selection

A correlation heatmap tells you which input features move together — and therefore which ones are redundant. The diverging colormap centered at zero makes positive and negative correlations immediately legible. Masking the upper triangle removes the redundant mirror and focuses the eye on the information.

```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# --- build correlation matrix ---
corr = df.corr()   # ← pandas DataFrame of pairwise Pearson correlations

# --- mask upper triangle (it's a mirror of the lower) ---
mask = np.triu(np.ones_like(corr, dtype=bool))   # ← True = masked out

fig, ax = plt.subplots(figsize=(10, 8))

sns.heatmap(
    corr,
    mask=mask,
    cmap='RdBu_r',          # ← diverging: red = positive, blue = negative
    center=0,               # ← white at correlation = 0
    vmin=-1, vmax=1,
    annot=True,             # ← print the correlation value in each cell
    fmt='.2f',              # ← 2 decimal places
    linewidths=0.5,
    linecolor='white',
    ax=ax
)

ax.set_title('Feature Correlation Matrix', fontsize=14, pad=12)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=150)
plt.show()
```

Reading the output: cells close to +1 (deep red) flag redundant features — adding both to a model rarely helps and often hurts. Cells near -1 (deep blue) flag inversely correlated features that might be worth combining. Cells near 0 (white) are independent.

---

## Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [02_customization_and_styling.md](./02_customization_and_styling.md) |
| ➡️ Next Topic | [04_seaborn_advanced.md](./04_seaborn_advanced.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
