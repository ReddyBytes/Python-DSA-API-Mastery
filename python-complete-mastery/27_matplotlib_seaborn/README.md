# 📈 Matplotlib and Seaborn for Data Science

---

Your manager says: "Show me how our model's accuracy changes with training data size."

You have the numbers in a pandas DataFrame. Now you need to turn those numbers into something a human can understand in 5 seconds. That's visualization.

A plot is not decoration. It is the fastest way to communicate a pattern, catch a bug, and convince a stakeholder. The question "why is the validation loss spiking?" gets answered by looking at a plot, not reading numbers. The question "is this feature useful?" gets answered faster by a histogram than by a correlation table.

**Matplotlib** is Python's foundational plotting library — full control, verbose syntax.
**Seaborn** is built on Matplotlib and adds statistical plots with beautiful defaults — concise syntax, professional output.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Line plots · Scatter plots · Histograms · Bar charts · `subplots` · Figure/Axes model · `set_xlabel` / `set_title` · `plt.tight_layout`

**Should Learn** — Important for real projects, comes up regularly:
Seaborn `heatmap` · `pairplot` · `boxplot` · `violinplot` · `histplot` · `scatterplot` · Color palettes · Figure sizing

**Good to Know** — Useful in specific situations:
Twin axes · Log scale · Annotations · `FuncAnimation` · Custom colormaps · `GridSpec` layouts

**Reference** — Know it exists, look up when needed:
3D plots (`mpl_toolkits.mplot3d`) · `matplotlib.patches` · Interactive backends · `Axes.inset_axes`

---

## 1️⃣ The Figure and Axes Model

Matplotlib has a two-level object model you must understand before anything else:

```
Figure  ← the entire canvas (page)
└── Axes ← a single plot (with its own x/y axes, labels, title)
    └── Artists (lines, patches, text, images)
```

```python
import matplotlib.pyplot as plt
import numpy as np

# Option A: Quick (implicit — pyplot manages current figure/axes)
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("Quick plot")
plt.show()

# Option B: Explicit (recommended for production code)
fig, ax = plt.subplots(figsize=(8, 5))   # ← create Figure and Axes explicitly
ax.plot([1, 2, 3], [4, 5, 6])           # ← call methods on the Axes object
ax.set_title("Explicit plot")
ax.set_xlabel("X axis")
ax.set_ylabel("Y axis")
plt.tight_layout()   # ← prevents label clipping
plt.savefig("plot.png", dpi=150, bbox_inches="tight")
plt.show()
```

**Always use the explicit `fig, ax = plt.subplots()` pattern** when writing reusable or multi-plot code. `plt.plot()` is fine for quick exploratory work.

---

## 2️⃣ Core Plots

### Line Plot — trends over time or index

```python
fig, ax = plt.subplots(figsize=(10, 4))

epochs = range(1, 21)
train_loss = [1.2 - 0.05*e + 0.01*np.random.randn() for e in epochs]
val_loss   = [1.3 - 0.04*e + 0.03*np.random.randn() for e in epochs]

ax.plot(epochs, train_loss, label="Train loss", color="steelblue", linewidth=2)
ax.plot(epochs, val_loss,   label="Val loss",   color="coral",     linewidth=2, linestyle="--")
ax.axhline(y=min(val_loss), color="gray", linestyle=":", alpha=0.7, label="Best val")

ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
ax.set_title("Training and Validation Loss")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
```

### Scatter Plot — relationships between two variables

```python
fig, ax = plt.subplots()

np.random.seed(42)
x = np.random.randn(100)
y = 0.8 * x + np.random.randn(100) * 0.5

scatter = ax.scatter(x, y, c=y, cmap="viridis", alpha=0.7, s=50)   # c= colors by value
plt.colorbar(scatter, label="y value")
ax.set_title("Scatter: x vs y (colored by y)")
```

### Histogram — distribution of one variable

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

data = np.concatenate([np.random.normal(0, 1, 700), np.random.normal(4, 0.5, 300)])

axes[0].hist(data, bins=50, edgecolor="white", color="steelblue")
axes[0].set_title("Histogram")

axes[1].hist(data, bins=50, density=True, edgecolor="white", color="steelblue")  # density=True → area sums to 1
axes[1].set_title("Density Histogram")

plt.tight_layout()
```

### Bar Chart — comparing categories

```python
categories = ["Linear\nRegression", "Random\nForest", "XGBoost", "Neural\nNet"]
accuracies = [0.82, 0.89, 0.91, 0.90]
errors     = [0.02, 0.015, 0.01, 0.025]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(categories, accuracies, yerr=errors, capsize=5,
              color=["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"], alpha=0.85)

ax.set_ylim(0.75, 0.95)
ax.set_ylabel("Accuracy")
ax.set_title("Model Comparison")

# Add value labels on bars
for bar, val in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
            f"{val:.0%}", ha="center", va="bottom", fontsize=10)
```

### Subplots — multiple plots in one figure

```python
fig, axes = plt.subplots(2, 3, figsize=(15, 8))   # 2 rows × 3 columns

axes[0, 0].plot([1, 2, 3], [4, 5, 6])
axes[0, 0].set_title("Plot 1")

axes[0, 1].scatter([1, 2, 3], [3, 2, 1])
axes[0, 1].set_title("Plot 2")

# Flatten for iteration
for i, ax in enumerate(axes.flatten()):
    ax.set_title(f"Subplot {i+1}")

# Hide unused axes
axes[1, 2].set_visible(False)

plt.suptitle("Multiple Subplots", fontsize=14)
plt.tight_layout()
```

---

## 3️⃣ Seaborn — Statistical Visualization

Seaborn's philosophy: one-line statistical plots with beautiful defaults.

```python
import seaborn as sns
import pandas as pd
import numpy as np

# Load a built-in dataset
df = sns.load_dataset("tips")   # restaurant tips data
```

### Distribution Plots

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Histogram + KDE
sns.histplot(df["total_bill"], kde=True, ax=axes[0])
axes[0].set_title("Total Bill Distribution")

# Box plot — shows quartiles and outliers
sns.boxplot(x="day", y="total_bill", data=df, ax=axes[1])
axes[1].set_title("Bill by Day")

# Violin plot — distribution shape + box plot
sns.violinplot(x="day", y="total_bill", hue="sex", data=df, split=True, ax=axes[2])
axes[2].set_title("Bill by Day and Gender")

plt.tight_layout()
```

### Correlation Heatmap — essential for EDA

```python
# Create correlation matrix
numeric_df = df.select_dtypes(include="number")
corr = numeric_df.corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr,
            annot=True,      # show numbers in cells
            fmt=".2f",       # 2 decimal places
            cmap="coolwarm", # diverging colormap centered at 0
            vmin=-1, vmax=1,
            square=True,
            ax=ax)
ax.set_title("Feature Correlation Matrix")
plt.tight_layout()
```

### Pairplot — all combinations at once

```python
# Great for initial EDA — shows all pairwise relationships
g = sns.pairplot(df[["total_bill", "tip", "size"]],
                 diag_kind="kde",     # distribution on diagonal
                 plot_kws={"alpha": 0.5})
g.fig.suptitle("Pairplot", y=1.02)
plt.show()
```

### Categorical Plots

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Count plot (like bar chart for counts)
sns.countplot(x="day", hue="sex", data=df, ax=axes[0])

# Regression plot (scatter + regression line)
sns.regplot(x="total_bill", y="tip", data=df, ax=axes[1], scatter_kws={"alpha": 0.4})
axes[1].set_title("Tip vs Bill with Regression Line")

plt.tight_layout()
```

---

## 4️⃣ Customization and Polish

```python
# Set global style
plt.style.use("seaborn-v0_8-darkgrid")   # or "ggplot", "fivethirtyeight"
sns.set_theme(style="whitegrid", palette="husl")

# Color palettes
sns.color_palette("husl", 8)         # 8 distinct colors
sns.color_palette("Blues", as_cmap=True)  # sequential
sns.color_palette("coolwarm", as_cmap=True)  # diverging

# Annotation
ax.annotate(
    "Outlier!",
    xy=(x_outlier, y_outlier),         # point to annotate
    xytext=(x_outlier + 0.5, y_outlier + 1),  # text position
    arrowprops=dict(arrowstyle="->", color="red"),
    color="red"
)

# Log scale
ax.set_xscale("log")
ax.set_yscale("log")
```

---

## Common Mistakes to Avoid ⚠️

- **Using `plt.plot()` in loops** without clearing figures: you'll overlay plots. Use `fig, ax = plt.subplots()` in each iteration.
- **Forgetting `plt.tight_layout()`**: without it, labels overlap the plot area.
- **Using default color cycles for accessibility**: use colorblind-friendly palettes. Seaborn's `"colorblind"` palette is accessible.
- **Bar chart for continuous data**: use histograms for distributions, bar charts for discrete categories only.
- **Not saving before showing**: `plt.savefig()` must come before `plt.show()` — `show()` clears the figure.

---

## 🗺️ Matplotlib & Seaborn Learning Path — Topic Files

| Order | Topic | File |
|---|---|---|
| 01 | Subplots and Layouts — GridSpec, mosaic, shared axes | [01_subplots_and_layouts.md](./01_subplots_and_layouts.md) |
| 02 | Customization and Styling — rcParams, annotations, twin axes | [02_customization_and_styling.md](./02_customization_and_styling.md) |
| 03 | Color and Colormaps — sequential, diverging, accessible palettes | [03_color_and_colormaps.md](./03_color_and_colormaps.md) |
| 04 | Seaborn Advanced — FacetGrid, PairGrid, regression plots | [04_seaborn_advanced.md](./04_seaborn_advanced.md) |
| 05 | ML Visualization — confusion matrix, ROC, learning curves | [05_ml_visualization.md](./05_ml_visualization.md) |
| 06 | Saving and Exporting — DPI, formats, publication quality | [06_saving_and_exporting.md](./06_saving_and_exporting.md) |

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
