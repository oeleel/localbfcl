# Berkeley Function Calling Leaderboard (BFCL) - Project Summary

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Evaluation Approaches](#evaluation-approaches)
3. [Current Issues and Status](#current-issues-and-status)

---

## Environment Setup

### Prerequisites
- **Python Version**: Python 3.10 (required)
- **Package Manager**: pip (with optional conda environment)
- **Operating System**: Linux/macOS (for local model hosting)

### Installation Methods

#### Method 1: Editable Installation (Recommended for Development)
```bash
# Create Conda environment
conda create -n BFCL python=3.10
conda activate BFCL

# Clone repository
git clone https://github.com/ShishirPatil/gorilla.git
cd gorilla/berkeley-function-call-leaderboard

# Install in editable mode
pip install -e .
```

#### Method 2: PyPI Installation (For End Users)
```bash
pip install bfcl-eval  # Note: NOT 'bfcl', but 'bfcl-eval'
```

**Important**: For PyPI installations, you **must** set the `BFCL_PROJECT_ROOT` environment variable:
```bash
export BFCL_PROJECT_ROOT=/path/to/your/project/directory
```

### Optional Dependencies

#### For Locally-Hosted Models
Choose one backend based on your GPU:

**vLLM** (supports older GPUs like T4/V100):
```bash
pip install -e .[oss_eval_vllm]
```

**SGLang** (faster, requires SM 80+ GPUs like Ampere):
```bash
pip install -e .[oss_eval_sglang]
```

Optional speedup for SGLang:
```bash
# Install flashinfer (see https://docs.flashinfer.ai/installation.html)
```

#### For WandB Logging
```bash
pip install -e .[wandb]
```

### Environment Configuration

#### 1. Project Root Directory
- **Editable installations**: Optional, defaults to `berkeley-function-call-leaderboard` directory
- **PyPI installations**: **Required** - set `BFCL_PROJECT_ROOT` environment variable

When set, this controls:
- `result/` folder location: `$BFCL_PROJECT_ROOT/result/`
- `score/` folder location: `$BFCL_PROJECT_ROOT/score/`
- `.env` file location: `$BFCL_PROJECT_ROOT/.env`

#### 2. Environment Variables (.env file)

**Location**:
- Editable: `berkeley-function-call-leaderboard/.env`
- PyPI: `$BFCL_PROJECT_ROOT/.env`

**Setup**:
```bash
# Copy example file
cp bfcl_eval/.env.example .env  # For editable
# OR
cp $(python -c "import bfcl_eval; print(bfcl_eval.__path__[0])")/.env.example $BFCL_PROJECT_ROOT/.env  # For PyPI
```

**Required API Keys** (depending on models used):
- `OPENAI_API_KEY` - For OpenAI models (GPT-4, GPT-4o, etc.)
- `ANTHROPIC_API_KEY` - For Claude models
- `GOOGLE_API_KEY` - For Gemini models
- `MISTRAL_API_KEY` - For Mistral models
- `OPENROUTER_API_KEY` - For OpenRouter models (Qwen via OpenRouter)
- `SERPER_API_KEY` - For web search (recommended, faster)
- `SERPAPI_API_KEY` - For web search (fallback)
- `WANDB_BFCL_PROJECT` - For WandB logging (format: `ENTITY:PROJECT`)

**Web Search Configuration**:
- Serper.dev (recommended): Set `SERPER_API_KEY`
- SerpAPI (fallback): Set `SERPAPI_API_KEY`
- System automatically uses Serper if available, falls back to SerpAPI

**Perturbation Configuration** (for web search robustness testing):
```bash
BFCL_ENABLE_RANDOM_INSERTION=true
BFCL_RANDOM_INSERTION_RATE=0.05  # 5% insertion rate
BFCL_RANDOM_INSERTION_TEXT_POOL="ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],...,***"
```

**Local Server Configuration** (for pre-existing endpoints):
```bash
LOCAL_SERVER_ENDPOINT=localhost
LOCAL_SERVER_PORT=1053
```

### Verification
```bash
# Verify installation
python -c "import bfcl_eval; print('BFCL installed successfully')"

# Verify OpenRouter handler (if using)
python -c "from bfcl_eval.model_handler.api_inference.openrouter import OpenRouterHandler; print('OpenRouter handler available')"
```

---

## Evaluation Approaches

### Overview
BFCL is a comprehensive evaluation framework for assessing Large Language Models' (LLMs) ability to invoke functions. It supports multiple evaluation methodologies tailored to different function calling scenarios.

### Test Categories

#### 1. Single-Turn Categories
- **Simple** (`simple_python`): Basic single function calls
- **Parallel** (`parallel`): Multiple functions called in parallel
- **Multiple** (`multiple`): Sequential multiple function calls
- **Parallel Multiple** (`parallel_multiple`): Combination of parallel and sequential calls
- **Language-Specific**: `simple_java`, `simple_javascript`

#### 2. Live Data Categories (BFCL V2)
- **Live Simple**: Real-world simple function calls
- **Live Multiple**: Real-world multiple function calls
- **Live Parallel**: Real-world parallel function calls
- **Live Parallel Multiple**: Real-world combined scenarios
- **Irrelevance Detection**: Models should NOT call functions when irrelevant
- **Relevance Detection**: Models should call functions when relevant (no exact answer checking)

#### 3. Multi-Turn Categories (BFCL V3)
- **Base Multi-Turn** (`multi_turn_base`): Foundational multi-turn interactions
- **Augmented Multi-Turn** (`multi_turn_augmented`): Complex scenarios with ambiguity, multi-hop reasoning
- **Long-Context**: Tests with overwhelming context (hundreds/thousands of items)
- **Composite**: Combines all multi-turn challenges

#### 4. Agentic Categories (BFCL V4)
- **Web Search** (`web_search`):
  - **Base/Snippet** (100): Models receive search engine snippets
  - **No Snippet** (100): Models must fetch and read full webpages
- **Memory** (`memory`): Tests persistent state management across:
  - **Vector Store** (155): Semantic similarity-based storage (FAISS)
  - **Key-Value Store** (155): Traditional key-value storage
  - **Recursive Summarization** (155): Memory through text summarization

#### 5. Format Sensitivity (Non-Scoring)
- Tests model robustness to 26 different prompt format variations
- Return format variations (Python, JSON, XML)
- Tool call tag presence
- System message variations

### Evaluation Methodologies

#### 1. AST-Based Evaluation (Single-Turn)
- **Method**: Abstract Syntax Tree (AST) comparison
- **Process**:
  1. Parse model output into AST
  2. Compare against ground truth AST
  3. Allow type flexibility (int → float conversion)
  4. String standardization (whitespace/punctuation normalization)
- **Categories**: Simple, Parallel, Multiple, Parallel Multiple, Live categories

#### 2. State-Based Evaluation (Multi-Turn)
- **Method**: Compare system state after each turn
- **Process**:
  1. Execute model's function calls
  2. Update system state
  3. Compare final state against ground truth
- **Limitation**: Doesn't work well when functions don't directly alter state

#### 3. Response-Based Evaluation (Multi-Turn)
- **Method**: Compare execution results directly
- **Process**:
  1. Execute model's function calls
  2. Compare execution results against ground truth
  3. Ground truth must be a strict subset of model result
- **Categories**: Multi-turn categories (both checkers must pass)

#### 4. Agentic Evaluation
- **Web Search**: 
  - Evaluates search query formulation
  - Tests information extraction from snippets or full pages
  - Handles real web content with noise/perturbations
- **Memory**:
  - Tests CRUD operations on different backends
  - Evaluates semantic retrieval accuracy
  - Tests summarization-based memory management

### Model Support

#### API-Based Models
- **OpenAI**: GPT-4, GPT-4o, GPT-4.1, GPT-5, o3, o4-mini
- **Anthropic**: Claude 3.5, Claude 4 (Opus, Sonnet, Haiku)
- **Google**: Gemini 2.5, Gemini 2.0
- **Mistral**: Mistral Large, Small, Medium, Nemo
- **Cohere**: Command R7B, Command A
- **Amazon**: Nova Pro, Lite, Micro
- **OpenRouter**: Qwen models (2.5, 2 series) via OpenAI-compatible API
- **Others**: Grok, Writer, Functionary, DeepSeek, GLM, Kimi, etc.

#### Locally-Hosted Models
- **Llama**: Meta Llama 3.1, 3.2, 3.3, 4 (Scout, Maverick)
- **Qwen**: Qwen3 series (0.6B to 235B)
- **Mistral**: Ministral
- **Phi**: Microsoft Phi-4, Phi-4-mini
- **Granite**: IBM Granite 3.1, 3.2, 20B
- **Others**: Gemma, MiniCPM, Falcon3, Hammer, Arch-Agent, etc.

#### Third-Party Inference Platforms
- **Novita AI**: For Llama-4 and QwQ models
- **OpenRouter**: For Qwen models (newly added)

### Execution Modes

#### Function Calling (FC) Mode
- Models use native function calling/tool use APIs
- Structured output with function names and parameters
- More efficient and reliable

#### Prompt Mode
- Models receive function documentation in prompts
- Must generate function calls as text
- More flexible but less reliable

### Workflow

#### 1. Generation Phase
```bash
# Single model, single category
bfcl generate --model MODEL_NAME --test-category CATEGORY

# Multiple models/categories
bfcl generate --model MODEL1,MODEL2 --test-category CAT1,CAT2

# With parallelization
bfcl generate --model MODEL_NAME --test-category CATEGORY --num-threads 4

# For local models
bfcl generate --model MODEL_NAME --test-category CATEGORY \
  --backend sglang --num-gpus 1 --gpu-memory-utilization 0.9
```

#### 2. Evaluation Phase
```bash
# Evaluate generated responses
bfcl evaluate --model MODEL_NAME --test-category CATEGORY

# Partial evaluation (for subset of entries)
bfcl evaluate --model MODEL_NAME --test-category CATEGORY --partial-eval
```

#### 3. Output Structure
```
result/
  MODEL_NAME/
    CATEGORY/
      BFCL_v4_CATEGORY_result.json

score/
  MODEL_NAME/
    CATEGORY/
      BFCL_v4_CATEGORY_score.json
  data_overall.csv
  data_live.csv
  data_non_live.csv
  data_multi_turn.csv
  data_agentic.csv
  data_format_sensitivity.csv
```

### Accuracy Calculation

#### Overall Accuracy Formula (BFCL V4)
- **Live**: 10%
- **Non-Live**: 10%
- **Irrelevance**: 10%
- **Multi-Turn**: 30%
- **Agentic**: 40%

This weighting emphasizes complex, multi-step agentic tasks as single-turn tasks approach saturation.

---

## Current Issues and Status

### Recent Changes (From Git Status)

#### 1. OpenRouter Integration (New)
- **Status**: ✅ Implemented
- **Files Modified**:
  - `bfcl_eval/model_handler/api_inference/openrouter.py` (new)
  - `bfcl_eval/model_handler/api_inference/__init__.py` (updated)
  - `bfcl_eval/constants/model_config.py` (updated)
  - `OPENROUTER_SETUP_GUIDE.md` (new)
- **Purpose**: Enable Qwen model evaluation via OpenRouter API
- **Models Added**: Qwen 2.5 and Qwen 2 series (7B, 14B, 32B, 72B) in both FC and Prompt modes
- **Configuration**: Requires `OPENROUTER_API_KEY` in `.env`

#### 2. Web Search Implementation
- **Status**: ✅ Functional with perturbation support
- **File**: `bfcl_eval/eval_checker/multi_turn_eval/func_source_code/web_search.py`
- **Features**:
  - Serper.dev integration (primary)
  - SerpAPI fallback
  - Random insertion perturbation for robustness testing
  - Error simulation framework (currently unused)
- **Note**: Random error simulation code exists but is not actively used (see TODO comments)

#### 3. README Updates
- **Status**: Modified (content updates)
- **File**: `README.md`
- **Changes**: Likely documentation improvements

#### 4. Run Instructions
- **Status**: New file
- **File**: `run_instructions.txt`
- **Content**: Quick reference for perturbation evaluation commands

### Known Issues and TODOs

#### 1. Function Name Handling (TODO)
- **Location**: `bfcl_eval/constants/model_config.py:91`
- **Issue**: `underscore_to_dot` flag only affects checker, not tool compilation
- **Impact**: Some models don't support '.' in function names, requiring '_' replacement
- **Status**: Needs tool compilation step update

#### 2. Random Error Simulation (Unused Feature)
- **Location**: `bfcl_eval/eval_checker/multi_turn_eval/func_source_code/web_search.py:35-40`
- **Issue**: Random generators for error simulation are defined but not used
- **Status**: Code exists but feature is disabled
- **Note**: Comment indicates "that feature is not currently used"

#### 3. Leaderboard Table Initialization (TODO)
- **Location**: `bfcl_eval/eval_checker/eval_runner.py:765`
- **Issue**: Should use `defaultdict` for leaderboard table initialization
- **Impact**: Minor code quality improvement

#### 4. Typo in README
- **Location**: `README.md:321`
- **Issue**: "Mkae sure" should be "Make sure"
- **Impact**: Minor documentation error

### Current Work in Progress

#### Perturbation Evaluation
- **Status**: Active development/testing
- **Evidence**: 
  - `result_perturbed/` and `score_perturbed/` directories exist
  - Results for `gpt-4o-mini-2024-07-18-FC` and `gpt-4.1-mini-2025-04-14-FC`
  - Focus on `web_search` category with base and no_snippet variants
- **Purpose**: Testing model robustness to noisy web content

### Architecture Notes

#### Model Handler System
- **Base Classes**:
  - `api_inference`: For API-based models
  - `local_inference`: For locally-hosted models
- **Handler Pattern**: Each model has a dedicated handler class
- **Configuration**: Centralized in `model_config.py` with `ModelConfig` dataclass

#### Evaluation Pipeline
1. **Generation**: Model handlers produce responses
2. **Storage**: Results saved in JSON format with inference logs
3. **Evaluation**: Category-specific checkers (AST, state-based, response-based)
4. **Scoring**: Accuracy calculation and CSV generation

### Best Practices

#### For API Models
- Start with `--num-threads 1` to avoid rate limits
- Monitor API usage and costs
- Use `--allow-overwrite` for regeneration

#### For Local Models
- Use SGLang for newer GPUs (SM 80+)
- Use vLLM for older GPUs (T4/V100)
- Adjust `--gpu-memory-utilization` to avoid OOM errors
- Use `--skip-server-setup` if you have a pre-existing endpoint

#### For Evaluation
- Use `--partial-eval` when evaluating subsets
- Check `score/` directory for detailed results
- Review inference logs in result JSON files for debugging

### Troubleshooting

#### Common Issues
1. **Missing API Keys**: Check `.env` file location and content
2. **Model Not Found**: Verify model name in `SUPPORTED_MODELS.md`
3. **Rate Limits**: Reduce `--num-threads` or wait
4. **OOM Errors**: Reduce `--gpu-memory-utilization` or use fewer GPUs
5. **File Not Found**: Check `BFCL_PROJECT_ROOT` is set correctly (PyPI installs)

#### Getting Help
- Check [README.md](./README.md) for detailed documentation
- Review [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines
- See [LOG_GUIDE.md](./LOG_GUIDE.md) for interpreting inference logs
- Visit [Discord](https://discord.gg/grXXvj9Whz) `#leaderboard` channel

---

## Summary

The Berkeley Function Calling Leaderboard is a mature, actively-maintained evaluation framework supporting:
- **100+ models** across API and local hosting
- **Multiple evaluation methodologies** (AST, state-based, response-based)
- **Comprehensive test categories** from simple to complex agentic scenarios
- **Flexible deployment** options (editable install, PyPI, various backends)
- **Recent additions**: OpenRouter integration, perturbation testing, format sensitivity

The project is in active development with recent focus on:
- Agentic evaluation (web search, memory)
- Model expansion (especially Qwen via OpenRouter)
- Robustness testing (perturbations)
- Code quality improvements

---

*Last Updated: Based on current codebase state and git status*
*For the latest information, refer to [CHANGELOG.md](./CHANGELOG.md) and [README.md](./README.md)*
