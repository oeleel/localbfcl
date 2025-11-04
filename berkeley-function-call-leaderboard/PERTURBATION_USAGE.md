# Running Evaluations with Perturbation (Keeping Both Results)

This guide shows how to run the same models with perturbation enabled while keeping the original results intact.

## Strategy

Use a separate result directory for perturbed results, so both versions are saved:
- **Original results**: `result/model-name/...`
- **Perturbed results**: `result_perturbed/model-name/...` or `result/model-name-perturbed/...`

## Step-by-Step Instructions

### 1. Enable Perturbation in `.env`

Add to your `.env` file:
```bash
# Enable random insertion perturbation
BFCL_ENABLE_RANDOM_INSERTION=true
BFCL_RANDOM_INSERTION_RATE=0.05
BFCL_RANDOM_INSERTION_TEXT_POOL="ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],...,***"
```

### 2. Generate Results with Perturbation (Custom Directory)

Use `--result-dir` to save to a separate directory:

```bash
# For gpt-4o-mini
bfcl generate \
  --model gpt-4o-mini-2024-07-18-FC \
  --test-category web_search \
  --num-threads 4 \
  --result-dir result_perturbed

# For gpt-4.1-mini
bfcl generate \
  --model gpt-4.1-mini-2025-04-14-FC \
  --test-category web_search \
  --num-threads 4 \
  --result-dir result_perturbed
```

### 3. Evaluate Perturbed Results

Use the same custom directory for evaluation:

```bash
# Evaluate gpt-4o-mini with perturbation
bfcl evaluate \
  --model gpt-4o-mini-2024-07-18-FC \
  --test-category web_search \
  --result-dir result_perturbed

# Evaluate gpt-4.1-mini with perturbation
bfcl evaluate \
  --model gpt-4.1-mini-2025-04-14-FC \
  --test-category web_search \
  --result-dir result_perturbed
```

### 4. Compare Results

After both evaluations complete, you'll have:

**Original Results:**
```
result/
├── gpt-4o-mini-2024-07-18-FC/
│   └── agentic/
│       ├── BFCL_v4_web_search_base_result.json
│       └── BFCL_v4_web_search_no_snippet_result.json
└── gpt-4.1-mini-2025-04-14-FC/
    └── agentic/
        ├── BFCL_v4_web_search_base_result.json
        └── BFCL_v4_web_search_no_snippet_result.json
```

**Perturbed Results:**
```
result_perturbed/
├── gpt-4o-mini-2024-07-18-FC/
│   └── agentic/
│       ├── BFCL_v4_web_search_base_result.json
│       └── BFCL_v4_web_search_no_snippet_result.json
└── gpt-4.1-mini-2025-04-14-FC/
    └── agentic/
        ├── BFCL_v4_web_search_base_result.json
        └── BFCL_v4_web_search_no_snippet_result.json
```

**Evaluation Scores:**
```
score/
├── data_overall.csv (contains both original and perturbed)
├── data_agentic.csv
└── ...

score_perturbed/
├── data_overall.csv (perturbed results only)
├── data_agentic.csv
└── ...
```

## Alternative: Use Suffix in Result Directory

If you prefer to keep everything in the same `result/` directory but with different names:

```bash
# Save perturbed results with a suffix
bfcl generate \
  --model gpt-4o-mini-2024-07-18-FC \
  --test-category web_search \
  --num-threads 4 \
  --result-dir result_perturbed

# Then manually rename or use symlinks if needed
```

## Batch Script Example

Here's a script to run both models with perturbation:

```bash
#!/bin/bash

# Enable perturbation
export BFCL_ENABLE_RANDOM_INSERTION=true
export BFCL_RANDOM_INSERTION_RATE=0.05

# Generate with perturbation
echo "Generating perturbed results for gpt-4o-mini..."
bfcl generate \
  --model gpt-4o-mini-2024-07-18-FC \
  --test-category web_search \
  --num-threads 4 \
  --result-dir result_perturbed

echo "Generating perturbed results for gpt-4.1-mini..."
bfcl generate \
  --model gpt-4.1-mini-2025-04-14-FC \
  --test-category web_search \
  --num-threads 4 \
  --result-dir result_perturbed

# Evaluate
echo "Evaluating perturbed results..."
bfcl evaluate \
  --model gpt-4o-mini-2024-07-18-FC,gpt-4.1-mini-2025-04-14-FC \
  --test-category web_search \
  --result-dir result_perturbed \
  --score-dir score_perturbed
```

## Disabling Perturbation

To run without perturbation (use original results directory):
```bash
# Disable in .env
BFCL_ENABLE_RANDOM_INSERTION=false

# Or just use default result directory
bfcl generate --model gpt-4o-mini-2024-07-18-FC --test-category web_search
```

## Notes

- The `--result-dir` and `--score-dir` options let you keep original and perturbed results completely separate
- Original results remain untouched in `result/`
- Both sets of results can be compared side-by-side
- Scores will be saved in separate directories for easy comparison

