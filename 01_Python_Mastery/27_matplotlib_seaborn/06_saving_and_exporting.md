# 🎯 Saving and Exporting Figures — From Notebook to Publication

A plot that only exists in a Jupyter notebook is a plot nobody else can use. Saving a figure correctly — right format, right resolution, right size — is what makes the difference between a chart that looks sharp in a paper and one that is blurry in a slide deck. Different outputs have different requirements: a blog post wants a compressed PNG, a paper wants a vector PDF at 300 DPI, a presentation wants a large high-contrast PNG.

---

## `plt.savefig()` — The Key Parameters

Every parameter in `savefig` has a purpose. Most figures look wrong in saved form because `bbox_inches='tight'` was omitted and axis labels got clipped, or because `dpi` was left at the default 100 and the result looked soft on a high-resolution display.

```python
plt.savefig('figure.png',
    dpi=300,                    # ← 72=screen, 150=web, 300=print/paper
    bbox_inches='tight',        # ← include all labels (prevents clipping)
    pad_inches=0.1,             # ← small padding around the tight bbox
    transparent=False,          # ← True for overlay on colored slides
    facecolor='white'           # ← set background color explicitly
)
```

`bbox_inches='tight'` is the single most important parameter. Without it, long axis labels, colorbars, and suptitles routinely get cut off in the saved file even though they look fine in the notebook.

---

## Format Guide

Choosing the wrong format is a one-way trip to a blurry figure or a bloated file. The rule of thumb: use **vector formats** (SVG, PDF) whenever the output will be resized, and use **raster formats** (PNG) when the size is fixed.

- **PNG**: raster, lossless. Best for web, Jupyter, general use. Use `dpi=150` for web, `dpi=300` for print.
- **SVG**: vector. Best for HTML/web — scalable, editable in Inkscape or Illustrator. No DPI setting needed.
- **PDF**: vector. Best for LaTeX papers. Fonts are embedded. No DPI setting needed.
- **JPEG**: raster, lossy. Smaller file but introduces compression artifacts on sharp edges and text — avoid for charts.
- **EPS**: legacy vector format for older journals that pre-date PDF submission systems.

```python
fig.savefig('figure.pdf')          # ← vector, for LaTeX
fig.savefig('figure.svg')          # ← vector, for web/HTML
fig.savefig('figure.png', dpi=300) # ← raster, for print
fig.savefig('figure.png', dpi=150) # ← raster, for web
```

---

## `tight_layout` vs `constrained_layout`

When a figure has multiple subplots, titles, and colorbars, the default spacing often causes elements to overlap. Two layout managers fix this automatically. **`tight_layout`** has been the standard for years; **`constrained_layout`** is the modern replacement that handles colorbars and nested gridspecs more reliably.

```python
plt.tight_layout()                          # ← adjusts subplot params to fit
fig = plt.figure(layout='constrained')      # ← modern replacement, handles colorbars better
fig, axs = plt.subplots(2, 2, layout='constrained')  # ← pass at creation time
```

Use `constrained_layout` for new code. It is enabled at figure creation time and cannot be switched on after the fact. `tight_layout()` is a one-time call that can be added at any point before saving.

---

## Saving Multi-Panel Figures

A dashboard or comparison figure involves multiple subplots in a single figure. The key is to call `fig.savefig()` — the method on the figure object — rather than `plt.savefig()`. When working in a loop or function, `plt.savefig()` saves whatever the current active figure is, which can be the wrong one.

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# ... fill plots ...
plt.tight_layout()
fig.savefig('dashboard.png', dpi=150, bbox_inches='tight')   # ← use fig.savefig, not plt.savefig
```

`figsize=(12, 10)` sets the physical size in inches. Combined with `dpi=150`, this produces a 1800×1500 pixel image — large enough for a presentation slide without being excessive.

---

## Closing Figures to Free Memory

Matplotlib keeps every figure in memory until explicitly closed. In a loop that generates hundreds of plots, this accumulates fast and eventually causes memory errors or notebook slowdowns. Close figures as soon as they have been saved.

```python
plt.close(fig)   # ← close specific figure
plt.close('all') # ← close all open figures (important in loops)
```

In a loop pattern:

```python
for name, subset in groups:
    fig, ax = plt.subplots()
    ax.plot(subset['x'], subset['y'])
    fig.savefig(f'{name}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)   # ← release memory immediately after saving
```

---

## DPI and figsize Relationship

**DPI** (dots per inch) and **figsize** (inches) combine to determine the pixel dimensions of a raster output. Understanding this relationship prevents the two most common mistakes: saving figures that are too small for print, and saving figures that are enormous and slow to render.

- Physical size in pixels = figsize (inches) x DPI
- `figsize=(6, 4), dpi=150` produces a 900x600 pixel image
- `figsize=(6, 4), dpi=300` produces a 1800x1200 pixel image
- For Retina/HiDPI displays: `dpi=200` or higher makes text and lines crisp
- For publication: check the journal's column width in centimeters, convert to inches (`cm / 2.54`), then set `dpi=300`

```python
# Single column in a typical journal: ~8.5 cm wide
fig, ax = plt.subplots(figsize=(8.5 / 2.54, 6 / 2.54))  # ← convert cm to inches
fig.savefig('single_column_figure.pdf')                  # ← vector, no DPI needed
```

For vector formats (PDF, SVG), DPI is irrelevant — the figure scales without loss. DPI only matters for raster formats.

---

## Real Workflow: Notebook to Publication

The typical workflow has two stages. In the exploratory stage, figures live in the notebook, update interactively, and resolution does not matter. In the final stage, figures are saved at publication quality and never regenerated by hand again — the save call is part of the script.

```python
# Notebook: exploratory
%matplotlib inline        # ← renders inline in Jupyter
plt.show()                # ← for scripts, opens interactive window

# Final: publication quality
fig.savefig('results/fig3_roc_curve.pdf',
            bbox_inches='tight',
            facecolor='white')
fig.savefig('results/fig3_roc_curve.png',
            dpi=300,
            bbox_inches='tight',
            facecolor='white')
plt.close(fig)
```

Save both a vector and a raster copy when you need the figure for multiple outputs: the PDF goes into the LaTeX paper, the PNG goes into the presentation. Never regenerate manually — keep the save call in the notebook so any future change flows through to both outputs automatically.

---

## Navigation

| | |
|---|---|
| 📖 Main README | [README.md](./README.md) |
| ⬅️ Prev Topic | [05_ml_visualization.md](./05_ml_visualization.md) |
| ➡️ Next Topic | [README.md](./README.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
