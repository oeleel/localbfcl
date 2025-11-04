# Web Search Content Perturbation Guide

## Random Insertion Perturbation

This guide explains how to use the random insertion perturbation feature for web search content evaluation.

## Overview

The random insertion perturbation adds random text snippets (like ads, promotional content, etc.) into web search results and webpage content. This helps test model robustness to noisy or misleading content.

## Configuration

The perturbation is controlled via environment variables in your `.env` file:

### Enable Random Insertion
```bash
BFCL_ENABLE_RANDOM_INSERTION=true
```

### Control Insertion Rate
The probability that a random insertion will be added after each word:
```bash
BFCL_RANDOM_INSERTION_RATE=0.05
```
- Default: `0.05` (5% chance per word)
- Range: `0.0` to `1.0`

### Customize Insertion Text Pool
The text snippets that will be randomly inserted:
```bash
BFCL_RANDOM_INSERTION_TEXT_POOL="ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],...,***"
```
- Default: `"ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],...,***"`
- Format: Comma-separated list of text snippets
- Each snippet will be inserted with spaces around it

## Example `.env` Configuration

```bash
# Enable random insertion perturbation
BFCL_ENABLE_RANDOM_INSERTION=true

# 5% insertion rate (inserts after ~5% of words)
BFCL_RANDOM_INSERTION_RATE=0.05

# Custom text pool with advertising-like snippets
BFCL_RANDOM_INSERTION_TEXT_POOL="ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],[Buy now],[Limited time],...,***"
```

## What Gets Perturbed

The random insertion is applied to:

1. **Search Result Snippets** (`search_engine_query`)
   - The `body` field of search results

2. **Webpage Content** (`fetch_url_content`)
   - All modes: `raw`, `markdown`, and `truncate`
   - The content returned in the `content` field

## Usage Examples

### Example 1: Light Perturbation (2% insertion rate)
```bash
# In .env file
BFCL_ENABLE_RANDOM_INSERTION=true
BFCL_RANDOM_INSERTION_RATE=0.02
```

### Example 2: Heavy Perturbation (10% insertion rate)
```bash
# In .env file
BFCL_ENABLE_RANDOM_INSERTION=true
BFCL_RANDOM_INSERTION_RATE=0.10
```

### Example 3: Custom Advertising Text Pool
```bash
# In .env file
BFCL_ENABLE_RANDOM_INSERTION=true
BFCL_RANDOM_INSERTION_RATE=0.05
BFCL_RANDOM_INSERTION_TEXT_POOL="SPONSORED CONTENT,ADVERTISEMENT,Click for more info,[Promoted],*Special Offer*"
```

## Running Evaluations with Perturbation

1. Add the configuration to your `.env` file
2. Run generation as normal:
   ```bash
   bfcl generate --model gpt-4o-mini-2024-07-18-FC --test-category web_search --num-threads 4
   ```
3. Run evaluation:
   ```bash
   bfcl evaluate --model gpt-4o-mini-2024-07-18-FC --test-category web_search
   ```

The perturbation is applied automatically when the environment variable is enabled.

## Disabling Perturbation

Set the environment variable to `false` or remove it:
```bash
BFCL_ENABLE_RANDOM_INSERTION=false
```

Or simply don't set it (default is `false`).

## Technical Details

- The perturbation uses a separate random generator (`_perturb_rng`) seeded with 42 for reproducibility when needed
- Insertions are added with spaces around them: `" word " + insertion_text + " word "`
- Only inserts after non-whitespace text segments (actual words/content)
- The perturbation is applied after content extraction but before returning to the model

## Example Output

**Original snippet:**
```
Elon Musk is the richest billionaire according to Forbes.
```

**With 5% insertion rate:**
```
Elon [Sponsored] Musk is the richest [Click here] billionaire according ADVERTISEMENT to Forbes.
```

