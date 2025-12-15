#!/bin/bash

# Script to rerun evaluations with proper conditions
# This will evaluate existing results (perturbation is applied during generation, not evaluation)

set -e

cd "$(dirname "$0")"

MODELS="gpt-4o-mini-2024-07-18-FC gpt-4.1-mini-2025-04-14-FC"
TEST_CATEGORIES="web_search_base web_search_no_snippet"

echo "=========================================="
echo "Evaluating UNPERTURBED results"
echo "=========================================="
echo ""

for model in $MODELS; do
    for category in $TEST_CATEGORIES; do
        echo "🦍 Model: $model"
        echo "🔍 Running test: $category"
        bfcl evaluate --model "$model" --test-category "$category" --result-dir result || echo "⚠️  Evaluation failed for $model $category"
        echo ""
    done
done

echo "=========================================="
echo "Evaluating PERTURBED results (0.05 rate)"
echo "=========================================="
echo ""

# Note: The perturbation was applied during generation, so we just evaluate
# The results in result_perturbed/ should have been generated with perturbation enabled
for model in $MODELS; do
    for category in $TEST_CATEGORIES; do
        echo "🦍 Model: $model"
        echo "🔍 Running test: $category (perturbed)"
        bfcl evaluate --model "$model" --test-category "$category" --result-dir result_perturbed --score-dir score_perturbed || echo "⚠️  Evaluation failed for $model $category"
        echo ""
    done
done

echo "=========================================="
echo "Evaluation complete!"
echo "=========================================="

