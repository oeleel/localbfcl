#!/bin/bash

# Quick script to check evaluation results

cd "$(dirname "$0")"

echo "=========================================="
echo "Checking Evaluation Results"
echo "=========================================="
echo ""

# Check if script is still running
if ps aux | grep -E "regenerate_with_perturbation|bfcl generate" | grep -v grep > /dev/null; then
    echo "⚠️  Script is still running..."
    echo ""
    tail -10 regeneration_log.txt 2>/dev/null || echo "No log file yet"
    echo ""
    echo "Check progress with: tail -f regeneration_log.txt"
    echo ""
else
    echo "✅ Script appears to be finished!"
    echo ""
fi

echo "=========================================="
echo "UNPERTURBED Results"
echo "=========================================="
echo ""

for model_dir in score_baseline/*/; do
    if [ -d "$model_dir" ]; then
        model=$(basename "$model_dir")
        echo "🦍 Model: $model"
        
        base_file="$model_dir/agentic/BFCL_v4_web_search_base_score.json"
        no_snippet_file="$model_dir/agentic/BFCL_v4_web_search_no_snippet_score.json"
        
        if [ -f "$base_file" ]; then
            base_acc=$(python3 -c "import json; f=open('$base_file'); d=json.load(f); print(f\"{d['accuracy']*100:.2f}% ({d['correct_count']}/{d['total_count']})\")" 2>/dev/null || echo "N/A")
            echo "  web_search_base: $base_acc"
        else
            echo "  web_search_base: Not found"
        fi
        
        if [ -f "$no_snippet_file" ]; then
            no_snippet_acc=$(python3 -c "import json; f=open('$no_snippet_file'); d=json.load(f); print(f\"{d['accuracy']*100:.2f}% ({d['correct_count']}/{d['total_count']})\")" 2>/dev/null || echo "N/A")
            echo "  web_search_no_snippet: $no_snippet_acc"
        else
            echo "  web_search_no_snippet: Not found"
        fi
        echo ""
    fi
done

echo "=========================================="
echo "PERTURBED Results (0.05 rate)"
echo "=========================================="
echo ""

for model_dir in score_perturbed_new/*/; do
    if [ -d "$model_dir" ]; then
        model=$(basename "$model_dir")
        echo "🦍 Model: $model"
        
        base_file="$model_dir/agentic/BFCL_v4_web_search_base_score.json"
        no_snippet_file="$model_dir/agentic/BFCL_v4_web_search_no_snippet_score.json"
        
        if [ -f "$base_file" ]; then
            base_acc=$(python3 -c "import json; f=open('$base_file'); d=json.load(f); print(f\"{d['accuracy']*100:.2f}% ({d['correct_count']}/{d['total_count']})\")" 2>/dev/null || echo "N/A")
            echo "  web_search_base: $base_acc"
        else
            echo "  web_search_base: Not found"
        fi
        
        if [ -f "$no_snippet_file" ]; then
            no_snippet_acc=$(python3 -c "import json; f=open('$no_snippet_file'); d=json.load(f); print(f\"{d['accuracy']*100:.2f}% ({d['correct_count']}/{d['total_count']})\")" 2>/dev/null || echo "N/A")
            echo "  web_search_no_snippet: $no_snippet_acc"
        else
            echo "  web_search_no_snippet: Not found"
        fi
        echo ""
    fi
done

echo "=========================================="
echo "File Locations:"
echo "=========================================="
echo ""
echo "Unperturbed scores:"
echo "  score_baseline/*/agentic/BFCL_v4_web_search_*_score.json"
echo ""
echo "Perturbed scores:"
echo "  score_perturbed_new/*/agentic/BFCL_v4_web_search_*_score.json"
echo ""
echo "Full log:"
echo "  regeneration_log.txt"
echo ""

