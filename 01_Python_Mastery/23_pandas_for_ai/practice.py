# Practice — Pandas for AI
# Full fine-tuning data preparation pipeline
# From raw messy data to clean JSONL ready for model training

import pandas as pd
import json
import os

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Create a sample AI training dataset
# ─────────────────────────────────────────────────────────────────────────────
# Simulates a real raw CSV you would download: messy, incomplete, unfiltered.

print("=" * 60)
print("SECTION 1 — Build sample raw dataset")
print("=" * 60)

raw_data = [
    # question,                         answer,                                     rating, source
    ("What is Python?",                 "A high-level programming language.",       5,      "wikipedia"),
    ("What is a neural network?",       "A system modeled on the human brain.",     5,      "arxiv"),
    ("What is backpropagation?",        "An algorithm to train neural networks.",   4,      "arxiv"),
    ("What is a tensor?",               "A multi-dimensional array.",               4,      "pytorch_docs"),
    ("What is overfitting?",            "When a model memorizes training data.",    5,      "wikipedia"),
    ("What is a transformer?",          "An attention-based architecture.",         5,      "arxiv"),
    ("What is Python?",                 "A scripting language.",                    3,      "stack_overflow"),  # duplicate question, lower quality
    ("What is gradient descent?",       "An optimization algorithm.",               4,      "wikipedia"),
    ("What is tokenization?",           None,                                       4,      "huggingface"),     # missing answer
    ("What is a loss function?",        "A measure of prediction error.",           5,      "wikipedia"),
    ("What is fine-tuning?",            "Training a pre-trained model on new data.",4,      "arxiv"),
    ("What is RAG?",                    "Retrieval-augmented generation.",           5,      "arxiv"),
    ("What is embeddings?",             "Dense vector representations of text.",    4,      "openai_docs"),
    ("What is a prompt?",               "Input text given to a language model.",    3,      "openai_docs"),
    ("What is temperature in LLMs?",    "Controls randomness of model output.",     4,      "openai_docs"),
    ("???",                             "Unknown.",                                  1,      "unknown"),         # junk question
    ("What is attention mechanism?",    "Allows model to focus on relevant parts.", 5,      "arxiv"),
    ("What is a vector database?",      "Stores and retrieves vector embeddings.",  4,      "pinecone_docs"),
    ("What is RLHF?",                   None,                                       "five", "arxiv"),           # missing answer AND string rating
    ("What is a context window?",       "Max tokens a model can process at once.",  4,      "openai_docs"),
    ("What is zero-shot learning?",     "Model performs task without examples.",    5,      "arxiv"),
    ("What is chain of thought?",       "Prompting technique using reasoning steps.",4,     "arxiv"),
    ("What is a vector database?",      "A database optimized for vector search.",  3,      "pinecone_docs"),   # duplicate question, lower quality
    ("What is model distillation?",     "Training a small model from a large one.", 4,      "wikipedia"),
    ("What is a hallucination in AI?",  "When a model generates false information.",5,      "arxiv"),
]

df_raw = pd.DataFrame(raw_data, columns=["question", "answer", "rating", "source"])

print(f"Raw dataset shape: {df_raw.shape}")
print()
print(df_raw.to_string())
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Inspect
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 2 — Inspect the raw dataset")
print("=" * 60)

print("--- head(3) ---")
print(df_raw.head(3))
print()

print("--- dtypes ---")
print(df_raw.dtypes)
print()

print("--- Missing values per column ---")
print(df_raw.isnull().sum())
print()

print("--- Rating value_counts (spot the string!) ---")
print(df_raw["rating"].value_counts())
print()

print("--- Duplicate questions ---")
print(f"Duplicate rows (full): {df_raw.duplicated().sum()}")
print(f"Duplicate questions:   {df_raw.duplicated(subset=['question']).sum()}")
print()

print("--- Describe (numeric only — rating is still mixed type) ---")
print(df_raw.describe(include="all"))
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Clean: fix types, handle nulls, remove duplicates
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 3 — Clean the dataset")
print("=" * 60)

df = df_raw.copy()

# Step 3a — Fix the rating column (convert strings like "five" to NaN)
print("Step 3a: Fix rating dtype")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
print(f"Rows with NaN rating after conversion: {df['rating'].isnull().sum()}")
print()

# Step 3b — Remove rows with missing answer or missing rating
print("Step 3b: Drop rows with missing answer or rating")
before = len(df)
df = df.dropna(subset=["answer", "rating"])
after = len(df)
print(f"Removed {before - after} rows. Remaining: {after}")
print()

# Step 3c — Now that nulls are gone, cast rating to int
df["rating"] = df["rating"].astype(int)
print("Step 3c: rating is now int")
print(df["rating"].dtype)
print()

# Step 3d — Remove junk questions (too short or just punctuation)
print("Step 3d: Remove junk questions (length <= 5)")
before = len(df)
df = df[df["question"].str.len() > 5]
after = len(df)
print(f"Removed {before - after} junk rows. Remaining: {after}")
print()

# Step 3e — Deduplicate: for duplicate questions, keep the one with highest rating
print("Step 3e: Deduplicate questions (keep highest-rated version)")
before = len(df)
df = df.sort_values("rating", ascending=False)
df = df.drop_duplicates(subset=["question"], keep="first")
df = df.reset_index(drop=True)
after = len(df)
print(f"Removed {before - after} duplicates. Remaining: {after}")
print()

print("--- Dataset after cleaning ---")
print(df.to_string())
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — Filter: keep only high-quality examples (rating >= 4)
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 4 — Filter for high-quality examples")
print("=" * 60)

df_quality = df[df["rating"] >= 4].copy()
df_quality = df_quality.reset_index(drop=True)

print(f"Rows with rating >= 4: {len(df_quality)}")
print()

print("--- Rating distribution after filtering ---")
print(df_quality["rating"].value_counts().sort_index(ascending=False))
print()

print("--- Source distribution ---")
print(df_quality["source"].value_counts())
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — Transform: format as prompt/completion pairs
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 5 — Transform: build prompt/completion pairs")
print("=" * 60)

def build_prompt(question: str) -> str:
    return f"Answer the following question clearly and accurately:\n\n{question}"

df_quality["prompt"]     = df_quality["question"].apply(build_prompt)
df_quality["completion"] = df_quality["answer"].str.strip()

print("--- Sample prompt/completion pairs ---")
for i, row in df_quality.head(3).iterrows():
    print(f"\nExample {i + 1}:")
    print(f"  prompt:     {row['prompt']!r}")
    print(f"  completion: {row['completion']!r}")
print()

# Keep only the columns needed for fine-tuning
df_final = df_quality[["prompt", "completion"]].copy()
print(f"Final dataset shape: {df_final.shape}")
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — Aggregation: understand the full dataset before exporting
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 6 — Aggregation summary")
print("=" * 60)

summary = df_quality.groupby("source").agg(
    count      = ("rating", "count"),
    avg_rating = ("rating", "mean"),
    max_rating = ("rating", "max"),
)
print("Examples per source:")
print(summary)
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — Export as JSONL (standard fine-tuning format)
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 7 — Export as JSONL")
print("=" * 60)

output_path = "fine_tuning_data.jsonl"

with open(output_path, "w") as f:
    for record in df_final.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

print(f"Exported {len(df_final)} examples to: {output_path}")
print()

# Verify: read back and inspect first 3 lines
print("--- Verifying output (first 3 lines) ---")
with open(output_path, "r") as f:
    for i, line in enumerate(f):
        obj = json.loads(line)
        print(f"Line {i + 1}: {obj}")
        if i >= 2:
            break
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — Bonus: export in OpenAI chat fine-tuning format (messages)
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 8 — Bonus: OpenAI chat fine-tuning format")
print("=" * 60)

chat_path = "fine_tuning_chat_format.jsonl"

with open(chat_path, "w") as f:
    for _, row in df_quality.iterrows():
        record = {
            "messages": [
                {"role": "system",    "content": "You are a helpful AI assistant."},
                {"role": "user",      "content": row["question"]},
                {"role": "assistant", "content": row["answer"].strip()},
            ]
        }
        f.write(json.dumps(record) + "\n")

print(f"Exported {len(df_quality)} examples in chat format to: {chat_path}")
print()

# Verify chat format
print("--- Chat format sample (first entry) ---")
with open(chat_path, "r") as f:
    sample = json.loads(f.readline())

for message in sample["messages"]:
    print(f"  [{message['role']}]: {message['content'][:80]}")
print()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — Pipeline summary
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("SECTION 9 — Full pipeline summary")
print("=" * 60)

print(f"  Raw rows:              {len(df_raw)}")
print(f"  After fixing types:    {len(df_raw)}  (no rows dropped, just dtype fixed)")
print(f"  After dropping nulls:  {len(df.dropna(subset=['answer', 'rating'])) + 2}")  # approximate
print(f"  After deduplication:   {len(df)}")
print(f"  After quality filter:  {len(df_quality)}")
print(f"  Final JSONL examples:  {len(df_final)}")
print()
print("Files written:")
print(f"  {output_path}       — prompt/completion format")
print(f"  {chat_path}  — OpenAI chat messages format")
print()
print("Pipeline complete. Data is ready for fine-tuning.")

# Cleanup output files (comment out if you want to keep them)
os.remove(output_path)
os.remove(chat_path)
