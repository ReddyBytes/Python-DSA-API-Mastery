# 🎯 Subplots and Layouts — Multi-Panel Figures

A newspaper front page doesn't show one giant story — it arranges multiple stories in a grid, each with the right amount of space. Multi-panel figures work the same way: you decide how many panels, how they relate to each other (shared axes? different sizes?), and where each story lives. Matplotlib gives you three tools of increasing power: `plt.subplots()` for simple grids, `GridSpec` for unequal-sized panels, and `subplot_mosaic` for named layouts.

---

## 🔲 1. `plt.subplots()` — The Everyday Tool

Think of `plt.subplots()` as ordering a pre-cut sheet of paper: you say "give me 2 rows and 3 columns" and you get back a neat grid where every panel is the same size. This covers 80% of real use cases. The returned `axes` array lets you loop over all panels without index math, and `sharex`/`sharey` links the zoom controls so panning one panel moves all the others.

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(
    nrows=2,
    ncols=3,
    figsize=(12, 6),       # ← total figure size in inches (width, height)
    sharex=True,           # ← all panels share the same x-axis zoom
    sharey=False,
)

x = np.linspace(0, 2 * np.pi, 200)

for i, ax in enumerate(axes.flat):   # ← .flat turns 2-D array into 1-D iterator
    ax.plot(x, np.sin(x + i * 0.5))
    ax.set_title(f"Panel {i}")

plt.tight_layout()
plt.show()
```

Key parameters at a glance:

| Parameter | What it does |
|---|---|
| `nrows`, `ncols` | Grid dimensions |
| `figsize` | `(width, height)` in inches |
| `sharex` | `True`, `False`, `'col'`, `'row'` |
| `sharey` | Same options as `sharex` |
| `squeeze` | `False` keeps axes always 2-D, prevents shape surprises |

---

## 📐 2. `GridSpec` — Unequal Panel Sizes

Sometimes your panels should not be equal — a wide summary chart on top, three detail charts below. **`GridSpec`** gives you a coordinate system where each panel can span multiple rows or columns, like a spreadsheet merge. You define the grid dimensions once, then "cut out" rectangles from it using Python slice notation.

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(10, 6))
gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.3)  # ← 2 rows, 3 cols, with spacing

ax_top   = fig.add_subplot(gs[0, :])      # ← row 0, all 3 columns (wide banner)
ax_bot_l = fig.add_subplot(gs[1, 0])      # ← row 1, col 0
ax_bot_m = fig.add_subplot(gs[1, 1])      # ← row 1, col 1
ax_bot_r = fig.add_subplot(gs[1, 2])      # ← row 1, col 2

x = np.linspace(0, 4, 100)
ax_top.plot(x, np.exp(-x), color='steelblue', label='Decay')
ax_top.set_title('Overview — Exponential Decay')
ax_top.legend()

for ax, label in zip([ax_bot_l, ax_bot_m, ax_bot_r], ['Detail A', 'Detail B', 'Detail C']):
    ax.scatter(np.random.rand(20), np.random.rand(20), s=20)
    ax.set_title(label)

plt.show()
```

You can also span rows: `gs[0:2, 0]` gives a tall left column next to shorter right panels — useful for a vertical feature importance bar chart beside multiple metric charts.

---

## 🗺️ 3. `subplot_mosaic` — Named Layouts

Slice notation works but it reads like assembly code. **`subplot_mosaic`** lets you draw the layout as ASCII art: each letter is a panel name, letters that repeat span that area, and `.` marks empty space. You get back a dictionary where keys are the letters you used, making the rest of your code self-documenting.

```python
# Layout: A spans the full top row; B is tall on the right; C and D share the bottom-left
layout = """
AAB
CDB
"""

fig, axd = plt.subplot_mosaic(layout, figsize=(10, 6), layout='constrained')

axd['A'].set_title('Wide top panel (A)')
axd['B'].set_title('Tall right panel (B)')
axd['C'].set_title('Bottom left (C)')
axd['D'].set_title('Bottom middle (D)')

# Access any panel by its letter key
axd['A'].plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))

plt.show()
```

This is the clearest choice when presenting to stakeholders: the layout string acts as a comment that explains the figure before anyone reads the code.

---

## 🔗 4. Shared Axes and Linked Zoom

When you have multiple time series — say training loss and validation accuracy over the same epochs — you want the x-axis to move together when you zoom or pan. **Shared axes** create a live link between panels: zooming one panel instantly updates all linked panels. Without shared axes, a reviewer might zoom into an interesting spike in one chart but lose context in the adjacent one.

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)  # ← sharex links zoom

epochs = np.arange(1, 51)
ax1.plot(epochs, np.exp(-epochs / 10) + 0.1 * np.random.rand(50), label='Train loss')
ax1.plot(epochs, np.exp(-epochs / 8) + 0.15 * np.random.rand(50), label='Val loss')
ax1.set_ylabel('Loss')
ax1.legend()

ax2.plot(epochs, 1 - np.exp(-epochs / 12), color='green', label='Accuracy')
ax2.set_ylabel('Accuracy')
ax2.set_xlabel('Epoch')
ax2.legend()

# Inspect the shared axis group programmatically
shared = ax1.get_shared_x_axes().get_siblings(ax1)  # ← returns all axes linked to ax1
print(f"Axes sharing x: {len(shared)}")

plt.tight_layout()
plt.show()
```

Use `sharex='col'` in `plt.subplots()` to link only within columns, or `sharex='row'` for row-level sharing — useful in grids where each row represents a different dataset.

---

## 🔍 5. Inset Axes

Sometimes a detail lives inside a larger chart — a zoomed-in view of a sharp loss spike within a full training curve. **Inset axes** are a mini-panel floating inside a parent axis. You place them using normalized figure coordinates: `[left, bottom, width, height]` where 0.0 is the left/bottom edge and 1.0 is the right/top edge of the parent axis.

```python
fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0, 100, 500)
y = np.exp(-x / 20) + 0.05 * np.random.rand(500)
ax.plot(x, y, color='steelblue')
ax.set_title('Training Loss with Inset Detail')
ax.set_xlabel('Steps')
ax.set_ylabel('Loss')

# Inset placed in upper-right corner of the parent axis
ax_inset = ax.inset_axes([0.55, 0.4, 0.4, 0.5])  # ← [x, y, width, height] in axis units

mask = x < 10  # ← zoom into the first 10 steps
ax_inset.plot(x[mask], y[mask], color='orange')
ax_inset.set_title('First 10 steps', fontsize=8)
ax_inset.tick_params(labelsize=7)

# Draw a box around the zoomed region in the main axis
ax.indicate_inset_zoom(ax_inset, edgecolor='orange')  # ← draws connecting lines

plt.tight_layout()
plt.show()
```

---

## 🧹 6. `tight_layout` vs `constrained_layout`

When you add axis labels and titles, they can overlap neighboring panels — the y-label of column 2 collides with the plots in column 1. Both `tight_layout` and `constrained_layout` solve this by automatically adding padding, but they use different algorithms.

**`tight_layout`** is the older approach: it runs as a post-processing step after you've built the figure, expanding the margins to fit labels. It works well for simple grids but can struggle with `GridSpec` spanning or colorbars.

**`constrained_layout`** is the modern replacement: it runs the layout engine continuously as you add elements, handles colorbars and `GridSpec` correctly, and is less likely to clip text. Set it at figure creation time.

```python
# Option 1 — tight_layout: call at the end, works for simple cases
fig, axes = plt.subplots(2, 2, figsize=(8, 6))
# ... plotting ...
plt.tight_layout(pad=1.5)   # ← pad controls spacing between panels

# Option 2 — constrained_layout: set when creating the figure (preferred)
fig, axes = plt.subplots(2, 2, figsize=(8, 6), layout='constrained')  # ← pass at creation
# ... plotting ...
# No need to call tight_layout — layout engine runs automatically
plt.show()

# Option 3 — set globally via rcParams
import matplotlib as mpl
mpl.rcParams['figure.constrained_layout.use'] = True  # ← applies to all subsequent figures
```

Rule of thumb: use `constrained_layout` for new work; use `tight_layout` when working with legacy code that you don't want to restructure.

---

## 🤖 7. Real ML Use Case — Training Dashboard

A complete training dashboard: 2×2 grid showing training loss, validation loss, accuracy curve, and a confusion matrix heatmap — all generated in one figure, properly labeled and linked.

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
epochs = np.arange(1, 31)

# Simulated training metrics
train_loss = np.exp(-epochs / 10) + 0.02 * np.random.rand(30)
val_loss   = np.exp(-epochs / 8)  + 0.05 * np.random.rand(30)
accuracy   = 1 - np.exp(-epochs / 9) - 0.02 * np.random.rand(30)

# Simulated 4-class confusion matrix
conf_matrix = np.array([
    [45,  3,  1,  1],
    [ 2, 38,  4,  2],
    [ 1,  3, 41,  5],
    [ 0,  2,  3, 49],
])

fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')  # ← 2x2 grid

# Panel 1 — training loss
axes[0, 0].plot(epochs, train_loss, color='steelblue', label='Train loss')
axes[0, 0].set_title('Training Loss')
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Loss')
axes[0, 0].legend()

# Panel 2 — validation loss
axes[0, 1].plot(epochs, val_loss, color='coral', label='Val loss')
axes[0, 1].set_title('Validation Loss')
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('Loss')
axes[0, 1].legend()

# Panel 3 — accuracy curve
axes[1, 0].plot(epochs, accuracy, color='mediumseagreen', label='Accuracy')
axes[1, 0].set_title('Accuracy')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('Accuracy')
axes[1, 0].set_ylim(0, 1)             # ← fix y range to [0, 1] for percentages
axes[1, 0].legend()

# Panel 4 — confusion matrix heatmap
im = axes[1, 1].imshow(conf_matrix, cmap='Blues')   # ← imshow renders a 2-D array as colors
fig.colorbar(im, ax=axes[1, 1])                      # ← attach colorbar to this specific axis
axes[1, 1].set_title('Confusion Matrix')
axes[1, 1].set_xlabel('Predicted')
axes[1, 1].set_ylabel('True')

# Annotate each cell with the count
for i in range(conf_matrix.shape[0]):
    for j in range(conf_matrix.shape[1]):
        axes[1, 1].text(j, i, str(conf_matrix[i, j]),
                        ha='center', va='center', color='black', fontsize=9)

fig.suptitle('Model Training Dashboard', fontsize=14, fontweight='bold')  # ← super-title over all panels
plt.show()
```

---

## 📂 Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [README.md](./README.md) |
| ➡️ Next Topic | [02_customization_and_styling.md](./02_customization_and_styling.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
