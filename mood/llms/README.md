# Crypto Market Mood Analyzer

This program aggregates crypto-market data from local JSON files and uses multiple Ollama models to perform sentiment analysis and predict "Market Mood".

## Features

- **Modular Architecture**: Data loading, preprocessing, Ollama orchestration, and aggregation.
- **Configurable Models**: Specify which Ollama model to use for each platform.
- **Weighted Aggregation**: Customizable weights for different data sources.
- **Batch Processing**: Handles large datasets efficiently with configurable batch sizes.
- **Concurrency**: Uses threading for parallel sentiment analysis.
- **Error Handling**: Logs errors and skips problematic entries.

## Setup

1. Ensure Ollama is installed and running on your system with the required models (e.g., `llama3.1`, `phi3`).
2. Install dependencies: `pip install -r requirements.txt`
3. Place your JSON data files in `../scrapper/data_sourcing/output/`

## Configuration

Edit the `CONFIG` dictionary in `market_mood_analyzer.py`:

- `data_dir`: Path to the data directory (relative to this script).
- `model_mapping`: Map platforms to Ollama models.
- `weights`: Weight for each platform in the final score.
- `batch_size`: Number of entries per batch.
- `system_prompt`: The prompt sent to Ollama models.

## Usage

Run the script:

```bash
python market_mood_analyzer.py
```

The program will:
- Load and preprocess data from JSON files.
- Analyze sentiment using Ollama models.
- Compute the global market mood score.
- Print a summary to console.
- Save detailed results to `final_mood_report.json`.

## Output

- **Console**: Summary with global mood score and interpretation.
- **JSON File**: Detailed report including all individual sentiment analyses.

## Mathematical Formula

The Global Mood Score \( M_G \) is calculated as:

\[ M_G = \frac{\sum_{i=1}^{n} (S_i \times W_p)}{\sum W_p} \]

Where:
- \( S_i \): Sentiment score for entry i (-1 to 1)
- \( W_p \): Weight for the platform of entry i

## Requirements

- Python 3.7+
- Ollama with configured models
- Dependencies: `ollama` library