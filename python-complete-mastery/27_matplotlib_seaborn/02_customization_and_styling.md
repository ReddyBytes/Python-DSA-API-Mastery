# 🎯 Customization and Styling — Making Figures Communication-Ready

A chart that is technically correct but visually confusing fails its purpose. Adding a title, labeling axes, choosing readable fonts, and highlighting key data points is the difference between a chart that confuses a stakeholder and one that closes a discussion. Matplotlib exposes every visual property — through `rcParams` for global defaults, style sheets for consistent themes, and per-element setters for surgical control.

---

## ⚙️ 1. `rcParams` — Global Defaults

Every property Matplotlib draws — font size, line width, figure size, tick direction — is stored in a global dictionary called **`rcParams`** (runtime configuration parameters). Changing a value in `rcParams` applies to every figure created after that point in the session, so you set it once at the top of a notebook rather than repeating the same keyword in every `ax.set()` call.

```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Set individual params by key
plt.rcParams['figure.figsize']    = (8, 4)     # ← default figure size for all new figures
plt.rcParams['font.size']         = 13         # ← base font size for all text elements
plt.rcParams['axes.labelsize']    = 12         # ← x/y axis label font size
plt.rcParams['axes.titlesize']    = 14         # ← subplot title font size
plt.rcParams['lines.linewidth']   = 2.0        # ← default line thickness
plt.rcParams['axes.spines.top']   = False      # ← remove top border for cleaner look
plt.rcParams['axes.spines.right'] = False      # ← remove right border

# Group-style shorthand using plt.rc()
plt.rc('font', family='sans-serif', size=12)   # ← set multiple font props at once
plt.rc('axes', grid=True, grid_alpha=0.3)      # ← enable light grid globally

# Restore all defaults when you want a clean slate
mpl.rcdefaults()  # ← resets rcParams to Matplotlib's built-in defaults
```

Commonly useful params for ML notebooks:

| `rcParams` key | Recommended value | Effect |
|---|---|---|
| `figure.figsize` | `(8, 4)` | Wider default |
| `font.size` | `12` or `13` | More readable in notebooks |
| `axes.prop_cycle` | custom color list | Consistent brand colors |
| `savefig.dpi` | `150` | Sharper inline images |
| `savefig.bbox` | `'tight'` | Never clip labels on save |

---

## 🎨 2. Style Sheets

**Style sheets** are pre-packaged `rcParams` bundles that apply a visual theme to all figures at once — the way a CSS stylesheet works for a webpage. Matplotlib ships with dozens of built-in styles including `ggplot`, `seaborn-v0_8`, `fivethirtyeight`, and `dark_background`. You can also load a custom `.mplstyle` file by path.

```python
# See all available styles
print(plt.style.available)   # ← prints the full list

# Apply a style globally for the rest of the session
plt.style.use('seaborn-v0_8')         # ← seaborn aesthetic on Matplotlib figures
plt.style.use('ggplot')               # ← R ggplot2-inspired style
plt.style.use('fivethirtyeight')      # ← bold colors, FiveThirtyEight look

# Stack multiple styles — later entries override earlier ones
plt.style.use(['seaborn-v0_8', 'seaborn-v0_8-paper'])  # ← combine base + paper variant

# Temporary style via context manager — reverts automatically when block exits
with plt.style.context('dark_background'):            # ← only affects this block
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    plt.show()
# Style is back to whatever was active before the with block
```

For ML projects, `seaborn-v0_8-whitegrid` is a strong default: clean white background with a subtle grid that helps readers track values without clutter.

---

## 📌 3. Annotations and Text

Raw lines and bars tell you what happened; **annotations** tell you why it matters. An annotation ties a text label to a specific data coordinate with an optional arrow, directing the reader's eye to the point you want them to notice — a sharp loss drop, a threshold crossing, or an outlier. Matplotlib separates three mechanisms: `ax.text()` for floating labels, `ax.annotate()` for pointed callouts, and `ax.axvline()`/`ax.axhline()` for reference lines.

```python
fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0, 50, 200)
y = np.exp(-x / 15) + 0.3

ax.plot(x, y, color='steelblue')
ax.set_title('Loss Curve with Annotations')

# Simple text label at a data coordinate
ax.text(25, 0.75, 'Plateau region', fontsize=10, color='gray')   # ← (x, y, label)

# Arrow annotation pointing from label to data point
ax.annotate(
    'Sharp early drop',
    xy=(3, y[12]),            # ← tip of the arrow (data coordinates)
    xytext=(10, 1.0),         # ← where the text sits
    arrowprops=dict(
        arrowstyle='->',
        color='darkred',
        lw=1.5,
    ),
    fontsize=10,
    color='darkred',
)

# Vertical reference line (e.g., epoch where you switched learning rate)
ax.axvline(x=20, color='orange', linestyle='--', linewidth=1.5, label='LR drop at step 20')
ax.legend()

plt.tight_layout()
plt.show()
```

---

## 🌈 4. Span Fills

Reference lines mark a single point; **span fills** shade a region — useful for showing confidence intervals, acceptable value ranges, or the overfitting zone in a training curve. `ax.axhspan()` shades a horizontal band across the full x range; `ax.fill_between()` shades the area between two y arrays along a shared x axis.

```python
fig, ax = plt.subplots(figsize=(8, 4))

epochs = np.arange(1, 51)
mean_acc = 1 - np.exp(-epochs / 10)
upper    = mean_acc + 0.04   # ← simulated upper confidence bound
lower    = mean_acc - 0.04   # ← simulated lower confidence bound

ax.plot(epochs, mean_acc, color='mediumseagreen', label='Mean accuracy')

# Shade the confidence interval between upper and lower bounds
ax.fill_between(
    epochs, lower, upper,
    alpha=0.25,                # ← transparency so the line stays visible
    color='mediumseagreen',
    label='95% CI',
)

# Shade a horizontal region (e.g., target accuracy range 0.90–0.95)
ax.axhspan(0.90, 0.95, alpha=0.1, color='gold', label='Target zone')  # ← horizontal band

ax.set_xlabel('Epoch')
ax.set_ylabel('Accuracy')
ax.set_title('Accuracy with Confidence Interval')
ax.legend()
plt.tight_layout()
plt.show()
```

---

## 🔀 5. Twin Axes

When two metrics share the same x-axis but live on completely different y scales — say training loss (small floats near zero) and batch throughput (hundreds of samples/sec) — stacking them on one y-axis crushes one signal into flatness. **Twin axes** solve this by overlaying two independent y-axes on the same x-axis. The two y-axes use different colors to help readers tell them apart.

```python
fig, ax1 = plt.subplots(figsize=(9, 4))

epochs = np.arange(1, 51)
loss   = np.exp(-epochs / 12) + 0.05 * np.random.rand(50)
acc    = 1 - np.exp(-epochs / 10)

# Primary y-axis — loss
ax1.plot(epochs, loss, color='steelblue', label='Loss')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')  # ← color y-tick labels to match line

# Secondary y-axis — shares x with ax1
ax2 = ax1.twinx()                                  # ← creates a new axis sharing the same x
ax2.plot(epochs, acc, color='coral', linestyle='--', label='Accuracy')
ax2.set_ylabel('Accuracy', color='coral')
ax2.tick_params(axis='y', labelcolor='coral')

# Combine both legends into one box
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')  # ← merged legend

ax1.set_title('Loss and Accuracy — Dual Y-Axis')
plt.tight_layout()
plt.show()
```

---

## 📊 6. Log Scales

Linear axes show absolute differences; **log scales** show relative (multiplicative) differences. This matters constantly in ML: learning rates span seven orders of magnitude (1e-7 to 1e-1), loss can drop from 10.0 to 0.001 in the same run, and model sizes vary from thousands to billions of parameters. On a linear axis, the small values at the bottom get crushed into a flat line — a log axis spreads them out proportionally.

```python
fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(10, 4))

steps = np.logspace(0, 4, 200)    # ← 1 to 10000, log-spaced
loss  = 10 / steps + 0.01 * np.random.rand(200)

# Linear scale — the interesting early drop is invisible
ax_lin.plot(steps, loss, color='steelblue')
ax_lin.set_title('Linear Scale — Early Drop Invisible')
ax_lin.set_xlabel('Steps')
ax_lin.set_ylabel('Loss')

# Log-log scale — the full decay is visible
ax_log.plot(steps, loss, color='coral')
ax_log.set_xscale('log')                   # ← log scale on x-axis
ax_log.set_yscale('log')                   # ← log scale on y-axis
ax_log.set_title('Log-Log Scale — Full Decay Visible')
ax_log.set_xlabel('Steps (log)')
ax_log.set_ylabel('Loss (log)')

plt.tight_layout()
plt.show()

# Learning rate range visualization (single log x-axis)
fig, ax = plt.subplots(figsize=(7, 3))
lrs  = np.logspace(-7, -1, 300)
perf = -np.log10(lrs) * 0.3 + 2 + 0.2 * np.random.rand(300)
ax.plot(lrs, perf)
ax.set_xscale('log')    # ← learning rate axis is almost always log scale
ax.set_xlabel('Learning Rate (log scale)')
ax.set_ylabel('Loss')
ax.set_title('LR Range Test')
plt.tight_layout()
plt.show()
```

---

## 📋 7. Custom Legends

The default legend works but often lands in the wrong place or gets cluttered. **Custom legends** let you control position, transparency, number of columns, font size, and what gets included. For multi-panel figures, `fig.legend()` creates a single shared legend rather than one per panel.

```python
fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x),           label='sin(x)',    color='steelblue')
ax.plot(x, np.cos(x),           label='cos(x)',    color='coral')
ax.plot(x, np.sin(x) * np.exp(-x / 5), label='Damped', color='mediumseagreen')

ax.legend(
    loc='upper right',     # ← position: 'best', 'upper left', 'lower center', etc.
    framealpha=0.6,        # ← legend box transparency (0 = invisible, 1 = opaque)
    ncol=3,                # ← arrange entries in 3 columns (horizontal layout)
    fontsize=9,
    title='Functions',
    title_fontsize=10,
)
plt.tight_layout()
plt.show()

# Multi-panel shared legend
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
line1, = ax1.plot([1, 2, 3], [1, 4, 9], label='Series A')
line2, = ax2.plot([1, 2, 3], [9, 4, 1], label='Series B')

fig.legend(
    handles=[line1, line2],           # ← explicitly pass handles from any panel
    loc='lower center',
    ncol=2,
    bbox_to_anchor=(0.5, -0.05),      # ← push legend below the figure
)
plt.tight_layout()
plt.show()
```

---

## 📐 8. Figure Sizing for Different Outputs

A figure that looks good in a Jupyter notebook at 96 DPI looks tiny in a paper column or pixelated in a slide deck. **Figure sizing** is output-dependent: notebooks want wider aspect ratios, publications need small physical sizes at high DPI (so text is legible when printed), and presentations need large figures where titles and labels are readable from the back of a room.

```python
# Jupyter notebook — wide and medium height, default DPI (96)
fig, ax = plt.subplots(figsize=(8, 4))              # ← standard notebook width
ax.plot([1, 2, 3], [1, 4, 9])
plt.show()

# Presentation slide — large, bold, visible from a distance
fig, ax = plt.subplots(figsize=(12, 6))             # ← wide slide format
plt.rcParams['font.size'] = 16                       # ← bigger font for readability
ax.plot([1, 2, 3], [1, 4, 9])
plt.tight_layout()
plt.show()

# Academic paper — small physical size, high DPI for print sharpness
fig, ax = plt.subplots(figsize=(3.5, 2.5))          # ← fits a single column (IEEE/NeurIPS)
ax.plot([1, 2, 3], [1, 4, 9])
plt.tight_layout()
fig.savefig('figure1.pdf', dpi=300, bbox_inches='tight')   # ← PDF for vector quality
fig.savefig('figure1.png', dpi=300, bbox_inches='tight')   # ← PNG for raster at 300 DPI
```

Quick reference:

| Output target | `figsize` | DPI | Format |
|---|---|---|---|
| Jupyter notebook | `(8, 4)` | 96 (default) | inline |
| Presentation | `(12, 6)` or `(10, 5)` | 150 | PNG/PDF |
| Paper (single col) | `(3.5, 2.5)` | 300 | PDF/EPS |
| Paper (full width) | `(7.0, 3.5)` | 300 | PDF/EPS |

---

## 🤖 9. Real ML Use Case — Annotated Training Curve

A fully styled training curve: twin axes for loss and accuracy, a vertical line where early stopping fired, a shaded overfitting region, and an annotation pointing to the best checkpoint.

```python
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')   # ← clean white background with grid
np.random.seed(7)

epochs = np.arange(1, 81)
train_loss = np.exp(-epochs / 18) + 0.02 * np.random.rand(80)
val_loss   = np.exp(-epochs / 15) + 0.04 * np.random.rand(80) + np.where(epochs > 45, (epochs - 45) * 0.005, 0)
accuracy   = 1 - np.exp(-epochs / 16) - 0.02 * np.random.rand(80)

best_epoch = int(np.argmin(val_loss)) + 1   # ← epoch with lowest validation loss
stop_epoch = 60                              # ← simulated early stopping trigger

fig, ax1 = plt.subplots(figsize=(10, 5), layout='constrained')

# Loss curves on primary axis
ax1.plot(epochs, train_loss, color='steelblue',  label='Train loss', linewidth=1.8)
ax1.plot(epochs, val_loss,   color='coral',      label='Val loss',   linewidth=1.8)
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Loss',  fontsize=12, color='dimgray')
ax1.tick_params(axis='y', labelcolor='dimgray')

# Accuracy on twin axis
ax2 = ax1.twinx()                                # ← overlay second y-axis
ax2.plot(epochs, accuracy, color='mediumseagreen', linestyle='--', label='Accuracy', linewidth=1.5)
ax2.set_ylabel('Accuracy', fontsize=12, color='mediumseagreen')
ax2.tick_params(axis='y', labelcolor='mediumseagreen')
ax2.set_ylim(0, 1.1)

# Shade overfitting region (after best epoch, val loss starts rising)
ax1.axvspan(best_epoch, stop_epoch, alpha=0.08, color='red', label='Overfitting region')  # ← horizontal span

# Mark early stopping with a vertical line
ax1.axvline(stop_epoch, color='darkorange', linestyle=':', linewidth=2, label=f'Early stop (ep {stop_epoch})')

# Annotate the best checkpoint
ax1.annotate(
    f'Best checkpoint\n(epoch {best_epoch})',
    xy=(best_epoch, val_loss[best_epoch - 1]),      # ← arrow tip at best point
    xytext=(best_epoch + 8, val_loss[best_epoch - 1] + 0.15),  # ← label offset
    arrowprops=dict(arrowstyle='->', color='black', lw=1.2),
    fontsize=9,
    color='black',
)

# Merge all legend handles from both axes
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(
    handles1 + handles2,
    labels1  + labels2,
    loc='upper right',
    framealpha=0.7,
    fontsize=9,
    ncol=2,
)

ax1.set_title('Training Dashboard — Loss, Accuracy, and Early Stopping', fontsize=13, fontweight='bold')
plt.show()
```

---

## 📂 Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [01_subplots_and_layouts.md](./01_subplots_and_layouts.md) |
| ➡️ Next Topic | [03_seaborn_statistical_plots.md](./03_seaborn_statistical_plots.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
