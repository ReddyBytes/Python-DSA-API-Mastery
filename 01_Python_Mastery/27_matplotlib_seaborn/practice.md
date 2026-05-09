# Matplotlib & Seaborn — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | subplots — create 2×2 grid with `layout='constrained'` | 🟢 |
| [Q2](#q2) | subplots — iterate axes with `.flat` and `sharex` | 🟢 |
| [Q3](#q3) | GridSpec — wide top panel + three equal bottom panels | 🟡 |
| [Q4](#q4) | subplot_mosaic — named layout with ASCII art string | 🟡 |
| [Q5](#q5) | inset axes — zoom detail inside main training curve | 🟠 |
| [Q6](#q6) | rcParams — set global font size, figure size, remove spines | 🟢 |
| [Q7](#q7) | style sheets — apply `seaborn-v0_8-whitegrid` via context manager | 🟢 |
| [Q8](#q8) | annotations — add arrow callout and `axvline` to a loss curve | 🟡 |
| [Q9](#q9) | twin axes — overlay loss and accuracy on same x-axis | 🟡 |
| [Q10](#q10) | log scales — compare linear vs log-log for decaying loss | 🟠 |
| [Q11](#q11) | named colors — bar chart with per-bar conditional coloring | 🟢 |
| [Q12](#q12) | colormap on scatter — encode a continuous variable with viridis | 🟢 |
| [Q13](#q13) | custom colorbar — attach labeled colorbar to heatmap axes | 🟡 |
| [Q14](#q14) | diverging vs sequential — correlation heatmap with `RdBu_r` | 🟡 |
| [Q15](#q15) | Normalize — apply `TwoSlopeNorm` for asymmetric residuals | 🟠 |
| [Q16](#q16) | pairplot — scatter matrix colored by class with KDE diagonal | 🟢 |
| [Q17](#q17) | heatmap with `annot` — correlation matrix with values printed | 🟢 |
| [Q18](#q18) | FacetGrid — histogram grid across model and dataset columns | 🟡 |
| [Q19](#q19) | violinplot via catplot — distribution split by hue | 🟡 |
| [Q20](#q20) | clustermap — hierarchically clustered correlation heatmap | 🟠 |
| [Q21](#q21) | confusion matrix heatmap — manual imshow with cell annotations | 🟢 |
| [Q22](#q22) | ROC curve — plot FPR vs TPR with random-classifier baseline | 🟡 |
| [Q23](#q23) | learning curve — train vs val with best-epoch marker | 🟡 |
| [Q24](#q24) | feature importance — sorted horizontal bar chart | 🟡 |
| [Q25](#q25) | residual plot — seaborn residplot with zero-line | 🟠 |
| [Q26](#q26) | savefig dpi and bbox_inches — save PNG at 300 DPI without clipping | 🟢 |
| [Q27](#q27) | save as PDF — vector output for LaTeX paper | 🟢 |
| [Q28](#q28) | PNG vs SVG tradeoffs — choose format for web vs print | 🟡 |
| [Q29](#q29) | tight_layout before save — fix overlapping labels in multi-panel figure | 🟡 |
| [Q30](#q30) | batch save — loop over groups, save one figure per group, close memory | 🟠 |

---

<a id="q1"></a>

### Q1 · subplots and layouts — create 2×2 grid with `layout='constrained'` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Create a 2×2 figure with `layout='constrained'`, figsize `(10, 8)`. Plot `sin(x)`, `cos(x)`, `sin(2x)`, and `cos(2x)` in each panel. Give each panel a title and add a super-title.


<details>
<summary>💡 Hint</summary>
Pass `layout='constrained'` to `plt.subplots()`. Index axes as `axes[row, col]`. Use `fig.suptitle()` for the super-title.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 200)
funcs = [np.sin(x), np.cos(x), np.sin(2*x), np.cos(2*x)]
titles = ['sin(x)', 'cos(x)', 'sin(2x)', 'cos(2x)']

fig, axes = plt.subplots(2, 2, figsize=(10, 8), layout='constrained')  # ← no tight_layout needed

for ax, y, title in zip(axes.flat, funcs, titles):  # ← .flat gives 1-D iterator over 2-D array
    ax.plot(x, y, color='steelblue')
    ax.set_title(title)

fig.suptitle('Trig Functions', fontsize=14, fontweight='bold')  # ← single title over all panels
plt.show()
```

**Why:** `layout='constrained'` handles spacing automatically and works correctly with colorbars and spanning panels — it is the modern replacement for `tight_layout`.
</details>

---

<a id="q2"></a>

### Q2 · subplots and layouts — iterate axes with `.flat` and `sharex` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Create a 2×3 grid with `sharex=True`. Plot six sine waves with phase shifts of `0, 0.5, 1.0, 1.5, 2.0, 2.5` radians. Use `axes.flat` to loop.


<details>
<summary>💡 Hint</summary>
`sharex=True` links all x-axis zoom controls. `axes.flat` converts a 2-D array to a flat iterator so you do not need index math.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 200)
phases = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

fig, axes = plt.subplots(2, 3, figsize=(12, 6),
                          sharex=True,   # ← pan/zoom one panel → all panels update
                          sharey=False)

for ax, phase in zip(axes.flat, phases):  # ← axes.flat: 1-D view of 2-D array
    ax.plot(x, np.sin(x + phase))
    ax.set_title(f'Phase = {phase:.1f} rad')

plt.tight_layout()
plt.show()
```

**Why:** `sharex=True` is essential when comparing time series — zooming one panel moves all others, preserving context across panels.
</details>

---

<a id="q3"></a>

### Q3 · subplots and layouts — GridSpec wide top panel + three bottom panels 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Use `fig.add_gridspec(2, 3)` to create a figure where the top panel spans all three columns and three equal panels sit in the bottom row. Plot an exponential decay in the top panel and scatter plots in each bottom panel.


<details>
<summary>💡 Hint</summary>
Use `gs[0, :]` for the top panel (slice notation means "all columns"). Use `gs[1, 0]`, `gs[1, 1]`, `gs[1, 2]` for the bottom three.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

fig = plt.figure(figsize=(10, 6))
gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.3)  # ← 2 rows, 3 cols, spacing

ax_top   = fig.add_subplot(gs[0, :])    # ← row 0, all 3 columns
ax_bot_l = fig.add_subplot(gs[1, 0])
ax_bot_m = fig.add_subplot(gs[1, 1])
ax_bot_r = fig.add_subplot(gs[1, 2])

x = np.linspace(0, 4, 100)
ax_top.plot(x, np.exp(-x), color='steelblue')
ax_top.set_title('Exponential Decay — Overview')

for ax, label in zip([ax_bot_l, ax_bot_m, ax_bot_r], ['Detail A', 'Detail B', 'Detail C']):
    ax.scatter(np.random.rand(20), np.random.rand(20), s=20)
    ax.set_title(label)

plt.show()
```

**Why:** GridSpec is the right tool whenever panels have unequal sizes — for example, a wide summary chart above three detail charts.
</details>

---

<a id="q4"></a>

### Q4 · subplots and layouts — subplot_mosaic named layout 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Use `plt.subplot_mosaic` with the layout string `"AAB\nCDB"` to create a figure where A spans the top-left, B spans the full right column, and C and D share the bottom-left. Title each panel with its letter.


<details>
<summary>💡 Hint</summary>
`subplot_mosaic` returns a dict keyed by the letters you used. Repeated letters span that area. Pass `layout='constrained'` to handle spacing.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

layout = """
AAB
CDB
"""

fig, axd = plt.subplot_mosaic(layout, figsize=(10, 6), layout='constrained')
# axd is a dict: keys are 'A', 'B', 'C', 'D'

axd['A'].set_title('Wide top-left (A)')
axd['B'].set_title('Tall right column (B)')
axd['C'].set_title('Bottom-left (C)')
axd['D'].set_title('Bottom-middle (D)')

x = np.linspace(0, 10, 100)
axd['A'].plot(x, np.sin(x))   # ← access any panel by its letter

plt.show()
```

**Why:** The layout string acts as a comment — it is self-documenting and more readable than equivalent GridSpec slice notation.
</details>

---

<a id="q5"></a>

### Q5 · subplots and layouts — inset axes with zoom detail 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Plot a full training loss curve (200 points, x from 0 to 100). Add an inset axis at `[0.55, 0.4, 0.4, 0.5]` showing only the first 10 steps. Use `ax.indicate_inset_zoom()` to draw connecting lines.


<details>
<summary>💡 Hint</summary>
`ax.inset_axes([x, y, width, height])` uses normalized axis coordinates (0 to 1). Then mask `x < 10` and plot the subset in the inset.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
x = np.linspace(0, 100, 500)
y = np.exp(-x / 20) + 0.05 * np.random.rand(500)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, y, color='steelblue')
ax.set_title('Training Loss with Inset Detail')
ax.set_xlabel('Steps'); ax.set_ylabel('Loss')

ax_inset = ax.inset_axes([0.55, 0.4, 0.4, 0.5])  # ← [left, bottom, width, height] in axis units

mask = x < 10
ax_inset.plot(x[mask], y[mask], color='orange')
ax_inset.set_title('First 10 steps', fontsize=8)
ax_inset.tick_params(labelsize=7)

ax.indicate_inset_zoom(ax_inset, edgecolor='orange')  # ← draws box + connecting lines

plt.tight_layout()
plt.show()
```

**Why:** Inset axes are the standard way to show a zoomed detail without creating a separate figure — useful for highlighting early training dynamics.
</details>

---

<a id="q6"></a>

### Q6 · customization — set global rcParams for font size, figure size, remove spines 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


At the top of a script, use `plt.rcParams` and `plt.rc()` to set: default figure size to `(8, 4)`, base font size to 13, and remove the top and right spines globally. Then create a simple line plot to verify the settings apply.


<details>
<summary>💡 Hint</summary>
`plt.rcParams['axes.spines.top'] = False` removes the top spine. `plt.rc('font', size=13)` sets multiple font properties at once.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['figure.figsize']    = (8, 4)    # ← default size for all new figures
plt.rcParams['font.size']         = 13        # ← base font size
plt.rcParams['axes.spines.top']   = False     # ← remove top border
plt.rcParams['axes.spines.right'] = False     # ← remove right border

plt.rc('axes', grid=True, grid_alpha=0.3)     # ← light grid globally

x = np.linspace(0, 10, 100)
fig, ax = plt.subplots()
ax.plot(x, np.sin(x))
ax.set_title('rcParams applied globally')
plt.show()
```

**Why:** Setting rcParams once at the top of a notebook is cleaner than repeating the same keyword arguments in every plot call.
</details>

---

<a id="q7"></a>

### Q7 · customization — apply style via context manager 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Plot the same sine wave twice: once with `'ggplot'` style and once with `'dark_background'` style — each in its own `with plt.style.context(...)` block so the styles do not leak between plots.


<details>
<summary>💡 Hint</summary>
`with plt.style.context('name'):` applies the style only inside the block and reverts automatically when the block exits.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 200)

with plt.style.context('ggplot'):          # ← style active only inside this block
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(x, np.sin(x))
    ax.set_title('ggplot style')
    plt.show()
# ← style reverts here

with plt.style.context('dark_background'): # ← different style, isolated
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(x, np.sin(x))
    ax.set_title('dark_background style')
    plt.show()
```

**Why:** The context manager form guarantees style isolation — essential in notebooks where style changes would otherwise persist for the rest of the session.
</details>

---

<a id="q8"></a>

### Q8 · customization — annotate loss curve with arrow callout and axvline 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Plot a loss curve that decays exponentially. Add: (1) an `ax.annotate()` arrow pointing to the sharp early drop, (2) an `ax.axvline()` at step 20 labeled "LR drop", and (3) a `ax.text()` label in the plateau region.


<details>
<summary>💡 Hint</summary>
`ax.annotate()` takes `xy` (arrow tip) and `xytext` (label position) in data coordinates. `arrowprops=dict(arrowstyle='->')` draws the arrow.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 50, 200)
y = np.exp(-x / 15) + 0.3

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, y, color='steelblue')
ax.set_title('Loss Curve with Annotations')

ax.text(25, 0.75, 'Plateau region', fontsize=10, color='gray')  # ← floating label

ax.annotate(
    'Sharp early drop',
    xy=(3, y[12]),          # ← arrow tip at this data point
    xytext=(10, 1.0),       # ← text sits here
    arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5),
    fontsize=10, color='darkred',
)

ax.axvline(x=20, color='orange', linestyle='--', linewidth=1.5, label='LR drop at step 20')
ax.legend()
plt.tight_layout()
plt.show()
```

**Why:** Annotations direct the reader's eye to the exact data point that matters — they are the difference between a descriptive chart and an explanatory one.
</details>

---

<a id="q9"></a>

### Q9 · customization — twin axes for loss and accuracy 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Create a figure with a primary y-axis for training loss and a secondary y-axis (using `ax1.twinx()`) for accuracy. Color the y-labels and tick labels to match their respective lines. Merge both legends into one box.


<details>
<summary>💡 Hint</summary>
`ax2 = ax1.twinx()` creates a new axis sharing the same x-axis. Use `ax1.get_legend_handles_labels()` and `ax2.get_legend_handles_labels()` then concatenate.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
epochs = np.arange(1, 51)
loss = np.exp(-epochs / 12) + 0.05 * np.random.rand(50)
acc  = 1 - np.exp(-epochs / 10)

fig, ax1 = plt.subplots(figsize=(9, 4))

ax1.plot(epochs, loss, color='steelblue', label='Loss')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')  # ← color the tick labels

ax2 = ax1.twinx()                                   # ← shares x-axis with ax1
ax2.plot(epochs, acc, color='coral', linestyle='--', label='Accuracy')
ax2.set_ylabel('Accuracy', color='coral')
ax2.tick_params(axis='y', labelcolor='coral')

# Merge legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

ax1.set_title('Loss and Accuracy — Dual Y-Axis')
plt.tight_layout()
plt.show()
```

**Why:** Twin axes prevent one metric from visually crushing the other when they live on different scales — the colored axes help viewers immediately know which side to read.
</details>

---

<a id="q10"></a>

### Q10 · customization — linear vs log-log comparison 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Create a side-by-side figure with two panels: the left shows a decaying loss on a linear axis, the right shows the same data on a log-log axis using `ax.set_xscale('log')` and `ax.set_yscale('log')`. Title both panels clearly.


<details>
<summary>💡 Hint</summary>
Generate x with `np.logspace(0, 4, 200)` for 1 to 10000. The interesting early drop is invisible on the linear scale but fully visible on the log-log scale.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

steps = np.logspace(0, 4, 200)
loss  = 10 / steps + 0.01 * np.random.rand(200)

fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(10, 4))

ax_lin.plot(steps, loss, color='steelblue')
ax_lin.set_title('Linear Scale — Early Drop Invisible')
ax_lin.set_xlabel('Steps'); ax_lin.set_ylabel('Loss')

ax_log.plot(steps, loss, color='coral')
ax_log.set_xscale('log')   # ← log scale on x
ax_log.set_yscale('log')   # ← log scale on y
ax_log.set_title('Log-Log Scale — Full Decay Visible')
ax_log.set_xlabel('Steps (log)'); ax_log.set_ylabel('Loss (log)')

plt.tight_layout()
plt.show()
```

**Why:** Log scales reveal proportional (multiplicative) differences that are invisible on linear axes — essential for loss curves, learning rates, and model sizes that span orders of magnitude.
</details>

---

<a id="q11"></a>

### Q11 · color — bar chart with per-bar conditional coloring 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Create a bar chart of model F1 scores. Color bars green (`'#4CAF50'`) when the score is above 0.85 and red (`'#F44336'`) when at or below 0.85. Add value labels above each bar.


<details>
<summary>💡 Hint</summary>
Use a list comprehension to build `bar_colors`. Call `ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + offset, ...)` to label each bar.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt

models = ['LR', 'RF', 'XGBoost', 'Neural Net']
scores = [0.78, 0.86, 0.90, 0.88]

bar_colors = ['#4CAF50' if v > 0.85 else '#F44336' for v in scores]  # ← conditional per-bar color

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(models, scores, color=bar_colors, edgecolor='white', width=0.6)

ax.set_ylim(0.6, 0.98)
ax.set_ylabel('F1 Score')
ax.set_title('Model F1 Comparison')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar, val in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
            f'{val:.2f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()
```

**Why:** Conditional coloring is immediate visual communication — a viewer sees at a glance which models pass the threshold without reading every number.
</details>

---

<a id="q12"></a>

### Q12 · color — scatter plot with continuous colormap 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Create a scatter plot of 200 random (x, y) points where a third variable `values` (random 0–1) is encoded by color using the `'viridis'` colormap. Attach a labeled colorbar.


<details>
<summary>💡 Hint</summary>
Pass `c=values, cmap='viridis'` to `ax.scatter()`. Then call `fig.colorbar(scatter, ax=ax, label='Score')` to attach the colorbar.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
x = np.random.randn(200)
y = np.random.randn(200)
values = np.random.rand(200)  # ← the variable encoded by color

fig, ax = plt.subplots(figsize=(7, 5))
scatter = ax.scatter(x, y, c=values, cmap='viridis', vmin=0, vmax=1, s=40, alpha=0.8)
fig.colorbar(scatter, ax=ax, label='Score')  # ← attach colorbar to this specific axis
ax.set_title('Scatter: viridis sequential colormap')
plt.tight_layout()
plt.show()
```

**Why:** `viridis` is perceptually uniform — equal steps in data produce equal perceived steps in color — and is safe for colorblind viewers and greyscale printing.
</details>

---

<a id="q13"></a>

### Q13 · color — diverging heatmap with labeled colorbar 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Create an 8×8 matrix of random values in `[-1, 1]`. Display it with `ax.imshow()` using the `'RdBu_r'` diverging colormap. Set `vmin=-1, vmax=1` so the center maps to white. Attach a colorbar labeled "Correlation".


<details>
<summary>💡 Hint</summary>
`cmap='RdBu_r'` reverses the colormap so red = positive, blue = negative. Always pass `vmin` and `vmax` to pin the center at zero.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

matrix = np.random.uniform(-1, 1, (8, 8))

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(matrix, cmap='RdBu_r', vmin=-1, vmax=1)  # ← _r reverses colormap
fig.colorbar(im, ax=ax, label='Correlation')             # ← attach to specific axis
ax.set_title('Diverging Colormap: RdBu_r')
plt.tight_layout()
plt.show()
```

**Why:** Without `vmin=-1, vmax=1`, Matplotlib maps the min/max of your specific matrix to the colormap endpoints — the center color won't correspond to zero unless the data happens to be symmetric.
</details>

---

<a id="q14"></a>

### Q14 · color — seaborn correlation heatmap with masked upper triangle 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Load a DataFrame with 4 numeric columns. Compute the correlation matrix, mask the upper triangle with `np.triu`, and display it using `sns.heatmap()` with `cmap='RdBu_r'`, `center=0`, `annot=True`, and `fmt='.2f'`.


<details>
<summary>💡 Hint</summary>
`mask = np.triu(np.ones_like(corr, dtype=bool))` creates a boolean matrix that is True in the upper triangle. Pass it to `sns.heatmap(mask=mask, ...)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

np.random.seed(42)
df = pd.DataFrame(np.random.randn(100, 4), columns=['A', 'B', 'C', 'D'])
df['C'] = 0.8 * df['A'] + 0.2 * np.random.randn(100)  # ← engineered correlation

corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))  # ← True = hidden (upper triangle)

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(corr, mask=mask, cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, annot=True, fmt='.2f',
            linewidths=0.5, linecolor='white', ax=ax)
ax.set_title('Feature Correlation Matrix')
plt.tight_layout()
plt.show()
```

**Why:** Masking the upper triangle removes the redundant mirror — the viewer's eye focuses on the information without visual repetition.
</details>

---

<a id="q15"></a>

### Q15 · color — TwoSlopeNorm for asymmetric residuals 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


You have a residuals array that ranges from -0.5 to +2.0 with a meaningful zero center. Apply `mcolors.TwoSlopeNorm(vmin=-0.5, vcenter=0, vmax=2.0)` to a heatmap so that zero always maps to the neutral white of the `'RdBu_r'` colormap even though the negative range is smaller.


<details>
<summary>💡 Hint</summary>
Import `matplotlib.colors as mcolors`. Pass `norm=norm_two` to `ax.imshow()` instead of `vmin`/`vmax`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# Asymmetric residuals: mostly positive, a few slightly negative
residuals = np.random.uniform(-0.5, 2.0, (6, 6))

norm_two = mcolors.TwoSlopeNorm(vmin=-0.5, vcenter=0, vmax=2.0)
# ← midpoint stays white at 0, even though the positive range (0 to 2) is 4x larger

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(residuals, cmap='RdBu_r', norm=norm_two)
fig.colorbar(im, ax=ax, label='Residual')
ax.set_title('TwoSlopeNorm: zero always maps to neutral white')
plt.tight_layout()
plt.show()
```

**Why:** Without `TwoSlopeNorm`, an asymmetric range would shift the colormap center away from zero — a viewer would misread "white" as a non-zero value.
</details>

---

<a id="q16"></a>

### Q16 · seaborn advanced — pairplot with KDE diagonal 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Load the iris dataset from sklearn. Build a DataFrame and add a `species` column. Call `sns.pairplot()` with `hue='species'`, `diag_kind='kde'`, `plot_kws={'alpha': 0.6}`, and `corner=True` to show only the lower triangle.


<details>
<summary>💡 Hint</summary>
`from sklearn.datasets import load_iris`. Use `iris.frame` to get a DataFrame. Map numeric target to species names before passing to pairplot.
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

iris = load_iris(as_frame=True)
df = iris.frame
df['species'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

sns.set_theme(style='ticks', font_scale=1.0)
g = sns.pairplot(
    df.drop(columns=['target']),
    hue='species',              # ← color by class label
    diag_kind='kde',            # ← KDE curve on the diagonal
    plot_kws={'alpha': 0.6, 's': 25},
    corner=True                 # ← lower triangle only
)
g.fig.suptitle('Iris Pairwise Feature Distributions', y=1.02)
plt.show()
```

**Why:** `pairplot` answers in one call: are the classes separable in any feature pair? Diagonal KDE curves that don't overlap identify the most discriminative features.
</details>

---

<a id="q17"></a>

### Q17 · seaborn advanced — heatmap with annotated values 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Create a 5×5 correlation matrix using random data. Display it with `sns.heatmap()`, setting `annot=True`, `fmt='.2f'`, `cmap='coolwarm'`, `vmin=-1`, `vmax=1`, and `square=True`.


<details>
<summary>💡 Hint</summary>
`annot=True` prints the value in each cell. `fmt='.2f'` formats floats to 2 decimal places. `square=True` forces equal cell dimensions.
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
df = pd.DataFrame(np.random.randn(100, 5), columns=list('ABCDE'))
corr = df.corr()

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(
    corr,
    annot=True,        # ← print the correlation value in each cell
    fmt='.2f',         # ← 2 decimal places
    cmap='coolwarm',
    vmin=-1, vmax=1,
    square=True,       # ← equal width and height per cell
    linewidths=0.5,
    ax=ax
)
ax.set_title('Correlation Heatmap with Annotations')
plt.tight_layout()
plt.show()
```

**Why:** `annot=True` is the difference between a colormap that forces the reader to look up the colorbar and one that is immediately readable — always use it for correlation matrices with fewer than ~15 features.
</details>

---

<a id="q18"></a>

### Q18 · seaborn advanced — FacetGrid histogram grid 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Create a DataFrame with columns `accuracy`, `model` (3 models), and `dataset` (2 datasets). Use `sns.FacetGrid` with `col='model'` and `row='dataset'` to plot a histogram of accuracy for each combination. Add axis labels and column/row titles.


<details>
<summary>💡 Hint</summary>
`g = sns.FacetGrid(df, col='model', row='dataset', height=3, aspect=1.2)` then `g.map(sns.histplot, 'accuracy', bins=15)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(0)
records = []
for model in ['LR', 'RF', 'XGB']:
    for dataset in ['Train', 'Test']:
        acc = np.random.normal(0.85 if model != 'LR' else 0.78, 0.05, 80)
        records += [{'model': model, 'dataset': dataset, 'accuracy': a} for a in acc]
df = pd.DataFrame(records)

g = sns.FacetGrid(df, col='model', row='dataset', height=3, aspect=1.2)
g.map(sns.histplot, 'accuracy', bins=15)  # ← apply the same plot to every cell
g.add_legend()
g.set_axis_labels('Accuracy', 'Count')
g.set_titles(col_template='{col_name}', row_template='{row_name}')
plt.show()
```

**Why:** FacetGrid replaces a manual loop over groups with a declarative grid definition — the result is consistent layout and shared axes with no index arithmetic.
</details>

---

<a id="q19"></a>

### Q19 · seaborn advanced — violinplot via catplot 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Use `sns.catplot()` with `kind='violin'` to compare accuracy distributions across three models. Set `hue='split'` for train/val/test coloring. Use `inner='quartile'` to show quartile lines inside the violin.


<details>
<summary>💡 Hint</summary>
`sns.catplot(data=df, x='model', y='accuracy', kind='violin', hue='split', inner='quartile', height=5)`
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(1)
records = []
for model in ['LR', 'RF', 'XGB']:
    for split in ['train', 'val', 'test']:
        base = {'LR': 0.78, 'RF': 0.87, 'XGB': 0.91}[model]
        acc = np.random.normal(base, 0.04, 60)
        records += [{'model': model, 'split': split, 'accuracy': a} for a in acc]
df = pd.DataFrame(records)

sns.catplot(
    data=df,
    x='model', y='accuracy',
    kind='violin',            # ← shows full distribution shape
    hue='split',
    inner='quartile',         # ← quartile lines inside violin body
    height=5, aspect=1.4
)
plt.title('Accuracy Distribution by Model and Split')
plt.show()
```

**Why:** `catplot` is the recommended entry point for multi-group categorical plots — it wraps FacetGrid internally so you can add `col=` or `row=` at any time without restructuring.
</details>

---

<a id="q20"></a>

### Q20 · seaborn advanced — clustermap 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Compute a 6×6 correlation matrix. Use `sns.clustermap()` to display it with `cmap='coolwarm'`, `center=0`, `row_cluster=True`, `col_cluster=True`, and `method='average'`. Set `figsize=(8, 8)`.


<details>
<summary>💡 Hint</summary>
`clustermap` reorders rows and columns by hierarchical clustering so that similar features appear adjacent — the dendrogram shows the grouping structure.
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.DataFrame(np.random.randn(100, 6), columns=list('ABCDEF'))
df['B'] = 0.9 * df['A'] + 0.1 * np.random.randn(100)  # ← A and B correlated
corr = df.corr()

g = sns.clustermap(
    corr,
    cmap='coolwarm',       # ← diverging: red = positive, blue = negative
    center=0,              # ← white at zero
    figsize=(8, 8),
    row_cluster=True,      # ← reorder rows by clustering
    col_cluster=True,      # ← reorder columns by clustering
    method='average',      # ← linkage method
    metric='euclidean'     # ← distance metric
)
g.fig.suptitle('Clustered Feature Correlations', y=1.02)
plt.show()
```

**Why:** Clustering reorders rows and columns so that groups of correlated features appear adjacent — structure that is hidden in a fixed-order heatmap becomes immediately visible.
</details>

---

<a id="q21"></a>

### Q21 · ML visualization — confusion matrix heatmap with cell annotations 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Build a 4×4 confusion matrix array manually. Display it with `ax.imshow(cm, cmap='Blues')`. Annotate every cell with the count using `ax.text()`, choosing white text when the cell value is above half the maximum and black text otherwise (auto-contrast).


<details>
<summary>💡 Hint</summary>
Loop `for i in range(n): for j in range(n):` and call `ax.text(j, i, cm[i, j], ha='center', va='center', color='white' if cm[i, j] > cm.max()/2 else 'black')`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

cm = np.array([
    [45,  3,  1,  1],
    [ 2, 38,  4,  2],
    [ 1,  3, 41,  5],
    [ 0,  2,  3, 49],
])
class_names = ['Cat', 'Dog', 'Bird', 'Fish']
n = len(class_names)

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap='Blues')
fig.colorbar(im, ax=ax)

ax.set_xticks(range(n)); ax.set_xticklabels(class_names, rotation=45)
ax.set_yticks(range(n)); ax.set_yticklabels(class_names)
ax.set_xlabel('Predicted'); ax.set_ylabel('True')
ax.set_title('Confusion Matrix')

for i in range(n):
    for j in range(n):
        ax.text(j, i, cm[i, j], ha='center', va='center',
                color='white' if cm[i, j] > cm.max() / 2 else 'black')  # ← auto-contrast

plt.tight_layout()
plt.show()
```

**Why:** Auto-contrast text ensures readability regardless of cell color — dark cells get white text, light cells get black text.
</details>

---

<a id="q22"></a>

### Q22 · ML visualization — ROC curve with random-classifier baseline 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Generate synthetic binary classification data with `make_classification`. Fit a Logistic Regression and compute `roc_curve` and `auc`. Plot the ROC curve with the AUC in the legend and a dashed diagonal baseline.


<details>
<summary>💡 Hint</summary>
`roc_curve(y_true, y_scores)` takes probability scores, not class labels. The dashed diagonal `ax.plot([0,1],[0,1],'k--')` represents a random classifier with AUC = 0.5.
</details>

<details>
<summary>✅ Answer</summary>

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)
y_scores = model.predict_proba(X_test)[:, 1]  # ← probability of positive class

fpr, tpr, _ = roc_curve(y_test, y_scores)
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, lw=2, label=f'Logistic Regression (AUC = {roc_auc:.2f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random classifier')  # ← diagonal baseline
ax.set_xlabel('False Positive Rate'); ax.set_ylabel('True Positive Rate')
ax.legend(); ax.set_title('ROC Curve')
plt.tight_layout()
plt.show()
```

**Why:** The further the curve bows toward the top-left corner, the better the separator. Any model worth deploying must curve above the dashed diagonal.
</details>

---

<a id="q23"></a>

### Q23 · ML visualization — learning curve with best-epoch marker 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Simulate train and validation loss over 50 epochs. Plot them on the same axes (solid train, dashed val). Add a vertical red dotted line at the epoch with the minimum validation loss. Shade a light confidence band using `ax.fill_between`.


<details>
<summary>💡 Hint</summary>
`best_epoch = int(np.argmin(val_loss)) + 1`. `ax.axvline(best_epoch, color='r', linestyle=':')`. `fill_between` takes two y arrays for the lower and upper bounds.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(7)
epochs = np.arange(1, 51)
train_loss = np.exp(-epochs / 18) + 0.02 * np.random.rand(50)
val_loss   = np.exp(-epochs / 15) + 0.04 * np.random.rand(50) + np.where(epochs > 35, (epochs - 35) * 0.005, 0)
best_epoch = int(np.argmin(val_loss)) + 1

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(epochs, train_loss, label='Train loss', color='steelblue')
ax.plot(epochs, val_loss, label='Val loss', color='coral', linestyle='--')
ax.axvline(best_epoch, color='red', linestyle=':', linewidth=2,
           label=f'Best epoch ({best_epoch})')               # ← marks checkpoint

ax.fill_between(epochs, val_loss - 0.02, val_loss + 0.02,   # ← confidence band
                alpha=0.2, color='coral')
ax.set_xlabel('Epoch'); ax.set_ylabel('Loss')
ax.set_title('Learning Curve')
ax.legend()
plt.tight_layout()
plt.show()
```

**Why:** The vertical best-epoch marker tells you exactly where to checkpoint the model. The divergence between train and val after that point is the visual signature of overfitting.
</details>

---

<a id="q24"></a>

### Q24 · ML visualization — sorted feature importance horizontal bar chart 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Given an array of 8 feature importances and their names, sort them by importance using `np.argsort()`. Plot a horizontal bar chart with `ax.barh()`. Set y-tick labels to the sorted feature names.


<details>
<summary>💡 Hint</summary>
`sorted_idx = np.argsort(importances)` gives ascending order — the most important feature ends up at the top of a `barh` chart. Use `np.array(feature_names)[sorted_idx]` to reorder names.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

feature_names = ['age', 'income', 'credit_score', 'num_loans',
                 'employment', 'debt_ratio', 'savings', 'years_employed']
importances = np.array([0.12, 0.25, 0.30, 0.08, 0.05, 0.10, 0.04, 0.06])

sorted_idx = np.argsort(importances)   # ← ascending: most important is last (→ top of barh)

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(range(len(sorted_idx)), importances[sorted_idx], align='center',
        color='steelblue', edgecolor='white')
ax.set_yticks(range(len(sorted_idx)))
ax.set_yticklabels(np.array(feature_names)[sorted_idx])  # ← sorted names on y-axis
ax.set_xlabel('Feature Importance')
ax.set_title('Random Forest Feature Importance')
plt.tight_layout()
plt.show()
```

**Why:** An unsorted feature importance chart is nearly unreadable. Sorting ascending with `barh` puts the most important feature at the top — the natural reading direction.
</details>

---

<a id="q25"></a>

### Q25 · ML visualization — seaborn residplot with zero-line 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Generate synthetic x and y data with a linear relationship plus noise. Fit the data conceptually (use `sns.residplot` which handles it internally). Add a red dashed zero-line with `ax.axhline(0)`. Explain in a comment what a random scatter vs a funnel pattern means.


<details>
<summary>💡 Hint</summary>
`sns.residplot(x='x', y='y', data=df, scatter_kws={'alpha': 0.4}, ax=ax)` plots residuals automatically. A funnel shape (spread increasing with x) indicates heteroscedasticity.
</details>

<details>
<summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.random.seed(42)
x = np.linspace(0, 10, 200)
y = 2 * x + 1 + np.random.normal(0, 1, 200)  # ← linear + noise
df = pd.DataFrame({'x': x, 'y': y})

fig, ax = plt.subplots(figsize=(8, 4))
sns.residplot(x='x', y='y', data=df,
              scatter_kws={'alpha': 0.4},  # ← semi-transparent to show density
              ax=ax)
ax.axhline(0, color='red', linestyle='--', linewidth=1.5)  # ← zero reference line

# Random scatter = good fit; funnel shape = heteroscedasticity (non-constant variance)
ax.set_title('Residual Plot — Random scatter = good fit')
ax.set_xlabel('x'); ax.set_ylabel('Residual')
plt.tight_layout()
plt.show()
```

**Why:** Residual plots are essential model diagnostics — visible patterns (funnel, curve) indicate the model is missing structure in the data that linear regression cannot capture.
</details>

---

<a id="q26"></a>

### Q26 · saving — savefig at 300 DPI with bbox_inches 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Create a simple line plot with a long y-axis label. Save it as `output.png` with `dpi=300`, `bbox_inches='tight'`, `pad_inches=0.1`, and `facecolor='white'`. Explain in a comment what happens if you omit `bbox_inches='tight'`.


<details>
<summary>💡 Hint</summary>
Always call `fig.savefig()` (not `plt.savefig()`) to save a specific figure object. `bbox_inches='tight'` expands the bounding box to include all labels.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, np.sin(x), color='steelblue')
ax.set_title('Sine Wave')
ax.set_xlabel('X Axis')
ax.set_ylabel('This is a very long y-axis label that would be clipped')

# Without bbox_inches='tight': long labels are clipped at the figure boundary
fig.savefig('output.png',
    dpi=300,               # ← 72=screen, 150=web, 300=print/paper
    bbox_inches='tight',   # ← include ALL labels — the most important parameter
    pad_inches=0.1,        # ← small padding around the tight bbox
    facecolor='white'      # ← explicit white background
)
plt.show()
```

**Why:** `bbox_inches='tight'` is the single most important `savefig` parameter — without it, long axis labels, colorbars, and suptitles are routinely clipped in the saved file.
</details>

---

<a id="q27"></a>

### Q27 · saving — save figure as vector PDF for LaTeX 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


Create a publication-style figure (figsize matching a single IEEE column: 3.5 × 2.5 inches). Plot a smooth curve and save it as both `figure.pdf` (vector) and `figure.png` (raster at 300 DPI). Close the figure after saving.


<details>
<summary>💡 Hint</summary>
PDF and SVG are vector formats — DPI is irrelevant because they scale without loss. For raster, `dpi=300` is the standard for papers. Always call `plt.close(fig)` after saving in scripts.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 5, 200)
fig, ax = plt.subplots(figsize=(3.5, 2.5))  # ← single IEEE column width
ax.plot(x, np.exp(-x) * np.cos(2 * np.pi * x), color='steelblue', linewidth=1.2)
ax.set_xlabel('Time (s)', fontsize=9)
ax.set_ylabel('Amplitude', fontsize=9)
ax.set_title('Damped Oscillation', fontsize=10)
plt.tight_layout()

fig.savefig('figure.pdf', bbox_inches='tight')          # ← vector, no DPI needed
fig.savefig('figure.png', dpi=300, bbox_inches='tight') # ← raster at 300 DPI
plt.close(fig)  # ← release memory; important in scripts generating many figures
```

**Why:** Save both formats — the PDF goes into the LaTeX paper, the PNG goes into the presentation. Keeping both save calls in the same cell guarantees they stay in sync.
</details>

---

<a id="q28"></a>

### Q28 · saving — PNG vs SVG tradeoffs 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Write a short code snippet that saves the same figure in PNG (dpi=150), SVG, and PDF formats. Then add comments explaining when to choose each: PNG for web, SVG for HTML with scaling, PDF for LaTeX, and why JPEG should be avoided for charts.


<details>
<summary>💡 Hint</summary>
The format is determined by the file extension. For SVG and PDF, DPI is ignored — they are vector formats that scale infinitely. JPEG introduces lossy compression artifacts on sharp edges.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 200)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, np.sin(x), color='steelblue', linewidth=2)
ax.set_title('Format Comparison')
plt.tight_layout()

# PNG — raster, lossless. Best for web, notebooks, general use.
fig.savefig('figure.png', dpi=150, bbox_inches='tight')

# SVG — vector. Best for HTML/web: scalable in browsers, editable in Inkscape.
fig.savefig('figure.svg', bbox_inches='tight')          # ← no DPI needed

# PDF — vector. Best for LaTeX papers: fonts embedded, no blurring at any zoom.
fig.savefig('figure.pdf', bbox_inches='tight')          # ← no DPI needed

# JPEG — avoid: lossy compression introduces artifacts on text and sharp edges.
# fig.savefig('figure.jpg')  ← do not use for charts

plt.close(fig)
```

**Why:** Format choice is output-dependent — vector for anything that will be resized or printed, raster for fixed-size web/notebook output.
</details>

---

<a id="q29"></a>

### Q29 · saving — fix overlapping labels with tight_layout before save 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


Create a 2×2 subplot grid with long axis labels and a suptitle. Demonstrate the problem (overlapping text) by NOT calling `tight_layout`, then fix it by adding `plt.tight_layout()` before `fig.savefig()`. Alternatively show the `layout='constrained'` approach.


<details>
<summary>💡 Hint</summary>
`plt.tight_layout(pad=1.5)` adds padding. `layout='constrained'` at figure creation time is the modern alternative that runs automatically and handles colorbars correctly.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)

# Option 1: tight_layout — classic approach, call before savefig
fig, axes = plt.subplots(2, 2, figsize=(9, 7))
for i, ax in enumerate(axes.flat):
    ax.plot(x, np.sin(x + i))
    ax.set_title(f'Panel {i}')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude (normalized)')

fig.suptitle('Multi-Panel Dashboard', fontsize=13, fontweight='bold')
plt.tight_layout(pad=1.5)                      # ← call BEFORE savefig
fig.savefig('tight_layout_demo.png', dpi=150, bbox_inches='tight')
plt.show()

# Option 2: constrained_layout — modern, set at creation time
fig2, axes2 = plt.subplots(2, 2, figsize=(9, 7), layout='constrained')  # ← pass here
for i, ax in enumerate(axes2.flat):
    ax.plot(x, np.sin(x + i))
    ax.set_title(f'Panel {i}')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude (normalized)')
fig2.suptitle('constrained_layout Demo', fontsize=13)
fig2.savefig('constrained_layout_demo.png', dpi=150, bbox_inches='tight')
plt.show()
```

**Why:** The most common cause of ugly saved figures is forgetting `tight_layout` — y-labels overlap plot areas and suptitles collide with panel titles.
</details>

---

<a id="q30"></a>

### Q30 · saving — batch save with plt.close() in a loop 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Given a dict of `{group_name: data_array}`, write a loop that creates one figure per group, plots a histogram, saves it to `{group_name}.png` at `dpi=150` with `bbox_inches='tight'`, and then closes the figure immediately with `plt.close(fig)`.


<details>
<summary>💡 Hint</summary>
Always close figures inside the loop body. Use `plt.close(fig)` to close the specific figure, not `plt.close('all')` (which would close anything else open). Failing to close in a long loop causes memory errors.
</details>

<details>
<summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
groups = {
    'model_A': np.random.normal(0.82, 0.05, 200),
    'model_B': np.random.normal(0.88, 0.04, 200),
    'model_C': np.random.normal(0.75, 0.07, 200),
}

for name, data in groups.items():
    fig, ax = plt.subplots(figsize=(6, 4))   # ← new figure per iteration
    ax.hist(data, bins=30, color='steelblue', edgecolor='white', alpha=0.85)
    ax.set_title(f'Accuracy Distribution — {name}')
    ax.set_xlabel('Accuracy'); ax.set_ylabel('Count')
    plt.tight_layout()
    fig.savefig(f'{name}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)   # ← release memory immediately; critical in long loops
    # plt.close('all') also works but is less precise

print("Saved 3 figures.")
```

**Why:** Matplotlib keeps every figure in memory until explicitly closed. In a loop over hundreds of groups, failing to close causes memory accumulation that eventually crashes the kernel.
</details>

---

> 📝 **Related theory files:**
> - Q1–Q5: [01_subplots_and_layouts.md](./01_subplots_and_layouts.md)
> - Q6–Q10: [02_customization_and_styling.md](./02_customization_and_styling.md)
> - Q11–Q15: [03_color_and_colormaps.md](./03_color_and_colormaps.md)
> - Q16–Q20: [04_seaborn_advanced.md](./04_seaborn_advanced.md)
> - Q21–Q25: [05_ml_visualization.md](./05_ml_visualization.md)
> - Q26–Q30: [06_saving_and_exporting.md](./06_saving_and_exporting.md)

---

## Navigation

| | |
|---|---|
| 📖 README | [README.md](./README.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Local Practice | [practice_local.py](./practice_local.py) |
