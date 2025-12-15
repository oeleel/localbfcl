# OpenRouter Setup Guide for BFCL

This guide will help you set up and use Qwen models via OpenRouter with the Berkeley Function Calling Leaderboard (BFCL) evaluation framework.

## Overview

OpenRouter provides an OpenAI-compatible API that allows you to access various models, including Qwen models, without needing to host them yourself. This is particularly useful when you don't have access to GPU servers or want to avoid the complexity of local model hosting.

## Prerequisites

1. **OpenRouter API Key**: You should already have an OpenRouter API key. If not, you can get one from [https://openrouter.ai/](https://openrouter.ai/)

2. **BFCL Installation**: Make sure you have BFCL installed. If not, follow the installation instructions in the main README.md

## Step-by-Step Setup

### Step 1: Set Up Environment Variables

1. Navigate to your BFCL project directory:
   ```bash
   cd berkeley-function-call-leaderboard
   ```

2. Create or edit the `.env` file in the project root. The `.env` file should be located at:
   - For editable installations: `berkeley-function-call-leaderboard/.env`
   - For PyPI installations: `$BFCL_PROJECT_ROOT/.env` (where `BFCL_PROJECT_ROOT` is your configured project root)

3. Add your OpenRouter API key to the `.env` file:
   ```bash
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

   **Important**: Replace `your_openrouter_api_key_here` with your actual OpenRouter API key.

### Step 2: Verify Installation

The OpenRouter handler has been added to the codebase. To verify everything is set up correctly, you can check if the handler is properly imported:

```bash
python -c "from bfcl_eval.model_handler.api_inference.openrouter import OpenRouterHandler; print('OpenRouter handler imported successfully')"
```

### Step 3: Available Qwen Models via OpenRouter

The following Qwen models are now available through OpenRouter:

#### Qwen 2.5 Models (Function Calling - FC):
- `qwen/qwen-2.5-72b-instruct-openrouter-FC`
- `qwen/qwen-2.5-32b-instruct-openrouter-FC`
- `qwen/qwen-2.5-14b-instruct-openrouter-FC`
- `qwen/qwen-2.5-7b-instruct-openrouter-FC`

#### Qwen 2.5 Models (Prompt Mode):
- `qwen/qwen-2.5-72b-instruct-openrouter`
- `qwen/qwen-2.5-32b-instruct-openrouter`
- `qwen/qwen-2.5-14b-instruct-openrouter`
- `qwen/qwen-2.5-7b-instruct-openrouter`

#### Qwen 2 Models (Function Calling - FC):
- `qwen/qwen-2-72b-instruct-openrouter-FC`
- `qwen/qwen-2-32b-instruct-openrouter-FC`
- `qwen/qwen-2-14b-instruct-openrouter-FC`
- `qwen/qwen-2-7b-instruct-openrouter-FC`

#### Qwen 2 Models (Prompt Mode):
- `qwen/qwen-2-72b-instruct-openrouter`
- `qwen/qwen-2-32b-instruct-openrouter`
- `qwen/qwen-2-14b-instruct-openrouter`
- `qwen/qwen-2-7b-instruct-openrouter`

**Note**: Models with `-FC` suffix are configured for Function Calling mode, while models without it are for Prompt mode.

### Step 4: Running Evaluations

#### Generate LLM Responses

To generate responses using a Qwen model via OpenRouter:

```bash
bfcl generate --model qwen/qwen-2.5-72b-instruct-openrouter-FC --test-category simple
```

You can specify multiple models and test categories:

```bash
bfcl generate \
  --model qwen/qwen-2.5-72b-instruct-openrouter-FC,qwen/qwen-2.5-32b-instruct-openrouter-FC \
  --test-category simple,parallel,multiple
```

#### Evaluate Generated Responses

After generating responses, evaluate them:

```bash
bfcl evaluate --model qwen/qwen-2.5-72b-instruct-openrouter-FC --test-category simple
```

### Step 5: Using Different Test Categories

Available test categories include:
- `simple` - Simple function calls
- `parallel` - Parallel function calls
- `multiple` - Multiple function calls
- `multi_turn` - Multi-turn conversations
- `web_search` - Web search functionality
- `memory` - Memory management
- And more...

See `TEST_CATEGORIES.md` for a complete list.

### Step 6: Controlling Parallelism

For API-based models like OpenRouter, you can control the number of parallel requests:

```bash
bfcl generate \
  --model qwen/qwen-2.5-72b-instruct-openrouter-FC \
  --test-category simple \
  --num-threads 4
```

**Important**: Adjust `--num-threads` based on your OpenRouter API rate limits. Start with `1` (default) and increase gradually if your API plan allows.

## Troubleshooting

### Issue: "OPENROUTER_API_KEY not found"

**Solution**: Make sure you've added `OPENROUTER_API_KEY` to your `.env` file and that the file is in the correct location (project root).

### Issue: "Model not found" or "Invalid model name"

**Solution**: 
1. Verify the model name is correct (check the list above)
2. Check if the model is available on OpenRouter by visiting [https://openrouter.ai/models](https://openrouter.ai/models)
3. Note that model availability may vary on OpenRouter

### Issue: Rate limit errors

**Solution**: 
1. Reduce `--num-threads` to 1
2. Check your OpenRouter account limits
3. Consider upgrading your OpenRouter plan if needed

### Issue: Authentication errors

**Solution**:
1. Verify your API key is correct in the `.env` file
2. Make sure there are no extra spaces or quotes around the API key
3. Check if your OpenRouter account has sufficient credits

## Adding More Models

If you want to use other Qwen models available on OpenRouter that aren't in the default list, you can:

1. Check available models on [OpenRouter's model page](https://openrouter.ai/models)
2. The model identifier format on OpenRouter is typically: `qwen/model-name`
3. You can use any OpenRouter model by creating a custom model configuration (see CONTRIBUTING.md for details)

## Cost Considerations

- OpenRouter charges per token usage
- Different models have different pricing
- Check [OpenRouter's pricing page](https://openrouter.ai/models) for current rates
- Monitor your usage through the OpenRouter dashboard

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Set up environment (one-time)
cd berkeley-function-call-leaderboard
echo "OPENROUTER_API_KEY=your_key_here" >> .env

# 2. Generate responses for a simple test category
bfcl generate \
  --model qwen/qwen-2.5-72b-instruct-openrouter-FC \
  --test-category simple \
  --num-threads 1

# 3. Evaluate the generated responses
bfcl evaluate \
  --model qwen/qwen-2.5-72b-instruct-openrouter-FC \
  --test-category simple

# 4. Check results
# Results will be in: result/qwen_qwen-2.5-72b-instruct-openrouter-FC/
# Scores will be in: score/qwen_qwen-2.5-72b-instruct-openrouter-FC/
```

## Additional Resources

- [BFCL Main README](./README.md) - General BFCL documentation
- [OpenRouter Documentation](https://openrouter.ai/docs) - OpenRouter API documentation
- [OpenRouter Models](https://openrouter.ai/models) - Available models and pricing
- [BFCL Contributing Guide](./CONTRIBUTING.md) - How to add new models or features

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the BFCL README for general issues
3. Check OpenRouter's status and documentation
4. Open an issue on the repository if it's a BFCL-specific problem

