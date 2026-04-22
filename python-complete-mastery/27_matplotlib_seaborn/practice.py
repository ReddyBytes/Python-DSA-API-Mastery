"""
Matplotlib and Seaborn — Practice Problems
Run each section independently to practice visualization.
"""

import matplotlib
matplotlib.use("Agg")   # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import pandas as pd

sns.set_theme(style="whitegrid")
SAVE = False   # set True to save plots to disk


def show_or_save(name):
    plt.tight_layout()
    if SAVE:
        plt.savefig(f"{name}.png", dpi=120, bbox_inches="tight")
    plt.close()


# ─────────────────────────────────────────────
# PROBLEM 1: Training Curve
# ─────────────────────────────────────────────
print("PROBLEM 1: Training Curve")

np.random.seed(42)
epochs = range(1, 51)
train_loss = [1.5 * np.exp(-0.08 * e) + 0.05 * np.random.randn() for e in epochs]
val_loss   = [1.6 * np.exp(-0.06 * e) + 0.1  + 0.05 * np.random.randn() for e in epochs]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(epochs, train_loss, label="Train", color="steelblue", linewidth=2)
ax.plot(epochs, val_loss,   label="Validation", color="coral", linewidth=2, linestyle="--")
ax.set_xlabel("Epoch"); ax.set_ylabel("Loss")
ax.set_title("Training and Validation Loss")
ax.legend()
ax.grid(alpha=0.3)
show_or_save("training_curve")
print("  ✓ Training curve created")


# ─────────────────────────────────────────────
# PROBLEM 2: Subplots Grid
# ─────────────────────────────────────────────
print("PROBLEM 2: Subplots Grid")

np.random.seed(0)
data = {
    "normal":      np.random.normal(0, 1, 1000),
    "bimodal":     np.concatenate([np.random.normal(-2, 0.5, 500), np.random.normal(2, 0.5, 500)]),
    "skewed":      np.random.exponential(1, 1000),
    "uniform":     np.random.uniform(-3, 3, 1000),
}

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, (name, d) in zip(axes.flatten(), data.items()):
    ax.hist(d, bins=40, color="steelblue", edgecolor="white", alpha=0.8)
    ax.set_title(f"{name.capitalize()} Distribution")
    ax.set_xlabel("Value"); ax.set_ylabel("Count")

plt.suptitle("Distribution Shapes", fontsize=14, y=1.02)
show_or_save("distributions")
print("  ✓ 4 distribution subplots created")


# ─────────────────────────────────────────────
# PROBLEM 3: Seaborn — Tips Dataset
# ─────────────────────────────────────────────
print("PROBLEM 3: Seaborn Tips Analysis")

tips = sns.load_dataset("tips")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

sns.histplot(tips["total_bill"], kde=True, ax=axes[0])
axes[0].set_title("Bill Distribution")

sns.boxplot(x="day", y="total_bill", data=tips, order=["Thur","Fri","Sat","Sun"], ax=axes[1])
axes[1].set_title("Bill by Day")

sns.scatterplot(x="total_bill", y="tip", hue="sex", style="smoker", data=tips, ax=axes[2], alpha=0.7)
axes[2].set_title("Tip vs Bill")

show_or_save("tips_analysis")
print("  ✓ Tips EDA plots created")


# ─────────────────────────────────────────────
# PROBLEM 4: Correlation Heatmap
# ─────────────────────────────────────────────
print("PROBLEM 4: Correlation Heatmap")

np.random.seed(42)
n = 200
df = pd.DataFrame({
    "feature_1": np.random.randn(n),
    "feature_2": np.random.randn(n),
})
df["feature_3"] = 0.8 * df["feature_1"] + 0.2 * np.random.randn(n)     # correlated with 1
df["target"]    = 0.5 * df["feature_1"] - 0.3 * df["feature_2"] + np.random.randn(n) * 0.5

corr = df.corr()

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax)
ax.set_title("Feature Correlation Matrix")
show_or_save("correlation_heatmap")
print("  ✓ Correlation heatmap created")
print(f"  feature_1 vs feature_3: {corr.loc['feature_1','feature_3']:.2f} (strong — engineered)")
print(f"  feature_1 vs target:    {corr.loc['feature_1','target']:.2f}")


# ─────────────────────────────────────────────
# PROBLEM 5: Model Comparison Bar Chart
# ─────────────────────────────────────────────
print("PROBLEM 5: Model Comparison Bar Chart")

models  = ["Logistic\nRegression", "Random\nForest", "XGBoost", "Neural\nNet"]
f1      = [0.78, 0.86, 0.90, 0.88]
colors  = ["#5C85D6", "#5CAD72", "#E08050", "#9B5CD6"]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(models, f1, color=colors, edgecolor="white", width=0.6)

ax.set_ylim(0.6, 0.95)
ax.set_ylabel("F1 Score", fontsize=12)
ax.set_title("Model F1 Score Comparison", fontsize=13)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

for bar, val in zip(bars, f1):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
            f"{val:.2f}", ha="center", va="bottom", fontsize=11)

show_or_save("model_comparison")
print("  ✓ Model comparison chart created")


# ─────────────────────────────────────────────
# PROBLEM 6: ROC Curve
# ─────────────────────────────────────────────
print("PROBLEM 6: ROC Curve")

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

fig, ax = plt.subplots(figsize=(7, 6))

for name, model in [("Logistic Regression", LogisticRegression()),
                    ("Random Forest", RandomForestClassifier(n_estimators=50))]:
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, proba)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, linewidth=2, label=f"{name} (AUC={roc_auc:.3f})")

ax.plot([0,1], [0,1], "k--", alpha=0.4, label="Random (AUC=0.500)")
ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves"); ax.legend(loc="lower right"); ax.grid(alpha=0.3)
show_or_save("roc_curves")
print("  ✓ ROC curves created")


print("\n✅ All visualization practice problems complete!")
