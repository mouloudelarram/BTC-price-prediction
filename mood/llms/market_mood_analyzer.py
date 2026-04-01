import os
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Configuration Section - Easily modifiable
CONFIG = {
    "data_dir": "../scrapper/data_sourcing/output",  # Relative path from mood/llms to data
    "model_mapping": {
        "fear_greed": "llama3.1",      # Model for Fear & Greed Index
        "coindesk": "llama3.1",        # Model for CoinDesk news
        "reddit": "phi3",              # Model for Reddit posts
        "truth_social": "phi3",        # Model for Truth Social posts
        "binance": "llama3.1",         # Model for Binance price data
        "coingecko": "llama3.1"        # Model for CoinGecko market data
    },
    "weights": {
        "fear_greed": 0.40,            # 40% weight for Fear & Greed
        "coindesk": 0.25,              # 25% weight for CoinDesk
        "reddit": 0.20,                # 20% weight for Reddit
        "truth_social": 0.20,          # 20% weight for Truth Social
        "binance": 0.15,               # 15% weight for Binance
        "coingecko": 0.15              # 15% weight for CoinGecko
    },
    "batch_size": 10,                  # Number of entries to process per batch
    "system_prompt": """
You are a sentiment analysis expert for cryptocurrency markets. Analyze the given content and provide a sentiment score for Bitcoin market mood.

Return ONLY a valid JSON object in this exact format:

{"sentiment_score": float between -1 and 1, "confidence": float between 0 and 1, "reasoning": "brief explanation"}

Where:
- sentiment_score: -1 (extremely bearish) to 1 (extremely bullish), 0 neutral
- confidence: how confident you are in the score (0 to 1)
- reasoning: short reason for the score

Do not include any other text or formatting.
"""
}

def load_data(data_dir: str) -> List[Dict[str, Any]]:
    """
    Scans the data directory for JSON files and loads all entries.
    Handles both list of objects and single object JSON files.
    """
    data = []
    if not os.path.exists(data_dir):
        logging.error(f"Data directory {data_dir} does not exist")
        return data

    for file in os.listdir(data_dir):
        if file.endswith('.json'):
            path = os.path.join(data_dir, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        data.extend(content)
                    elif isinstance(content, dict):
                        data.append(content)
                    else:
                        logging.warning(f"Unexpected JSON structure in {file}")
            except Exception as e:
                logging.error(f"Error loading {file}: {e}")
    return data

def preprocess_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and cleans content, platform, and metadata from an entry.
    Cleans text by removing URLs and normalizing whitespace.
    """
    content = entry.get('content', '')
    # Clean text: remove URLs and excessive whitespace
    content = re.sub(r'http\S+', '', content)
    content = re.sub(r'\s+', ' ', content).strip()

    return {
        'platform': entry.get('platform'),
        'content': content,
        'metadata': entry.get('metadata', {})
    }

def analyze_sentiment(content: str, model: str, system_prompt: str) -> Dict[str, Any]:
    """
    Sends content to Ollama model for sentiment analysis.
    Returns the parsed JSON response or None on error.
    """
    try:
        import ollama  # Import here to avoid issues if not installed
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': content}
            ]
        )
        result_text = response['message']['content'].strip()
        # Ensure it's valid JSON
        result = json.loads(result_text)
        # Validate structure
        if not all(k in result for k in ['sentiment_score', 'confidence', 'reasoning']):
            raise ValueError("Invalid response structure")
        return result
    except Exception as e:
        logging.error(f"Error analyzing sentiment with model {model}: {e}")
        return None

def process_batch(batch: List[Dict[str, Any]], model_mapping: Dict[str, str], system_prompt: str) -> List[Dict[str, Any]]:
    """
    Processes a batch of entries concurrently using ThreadPoolExecutor.
    """
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for entry in batch:
            platform = entry['platform']
            model = model_mapping.get(platform, 'llama3.1')  # Default model
            future = executor.submit(analyze_sentiment, entry['content'], model, system_prompt)
            futures.append((future, entry))

        for future, entry in futures:
            result = future.result()
            if result:
                results.append({
                    'entry': entry,
                    'sentiment': result
                })
            else:
                logging.warning(f"Failed to analyze entry for platform {entry['platform']}")
    return results

def aggregate_mood(results: List[Dict[str, Any]], weights: Dict[str, float]) -> float:
    """
    Aggregates sentiment scores into a global market mood score using weighted average.
    Formula: M_G = Σ(S_i * W_p) / Σ(W_p)
    """
    weighted_sum = 0.0
    total_weight = 0.0
    for res in results:
        platform = res['entry']['platform']
        score = res['sentiment']['sentiment_score']
        weight = weights.get(platform, 0.1)  # Default weight if not specified
        weighted_sum += score * weight
        total_weight += weight
    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight

def main():
    """
    Main function to orchestrate the entire pipeline.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load data
    data = load_data(CONFIG['data_dir'])
    logging.info(f"Loaded {len(data)} entries from data directory")

    # Preprocess data
    preprocessed = [preprocess_entry(e) for e in data if e.get('platform') and e.get('content')]
    logging.info(f"Preprocessed {len(preprocessed)} valid entries")

    # Batch processing
    batch_size = CONFIG['batch_size']
    all_results = []
    total_batches = (len(preprocessed) + batch_size - 1) // batch_size
    for i in range(0, len(preprocessed), batch_size):
        batch = preprocessed[i:i + batch_size]
        batch_num = i // batch_size + 1
        logging.info(f"Processing batch {batch_num}/{total_batches}")
        results = process_batch(batch, CONFIG['model_mapping'], CONFIG['system_prompt'])
        all_results.extend(results)

    # Aggregate mood
    global_mood = aggregate_mood(all_results, CONFIG['weights'])
    logging.info(f"Global Market Mood Score: {global_mood:.4f}")

    # Prepare report
    report = {
        'global_mood_score': global_mood,
        'total_entries_processed': len(all_results),
        'weights_used': CONFIG['weights'],
        'model_mapping_used': CONFIG['model_mapping'],
        'results': all_results  # Includes all individual results
    }

    # Save report
    with open('final_mood_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Console output
    print("\n" + "="*50)
    print("CRYPTO MARKET MOOD ANALYSIS REPORT")
    print("="*50)
    print(f"Global Market Mood Score: {global_mood:.4f}")
    print(f"Interpretation: {'Bullish' if global_mood > 0.1 else 'Bearish' if global_mood < -0.1 else 'Neutral'}")
    print(f"Total entries processed: {len(all_results)}")
    print("Report saved to: final_mood_report.json")
    print("="*50)

if __name__ == "__main__":
    main()