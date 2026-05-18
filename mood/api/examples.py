"""
Example script showing how to use the Mood Analysis Client.
"""

import asyncio
from client import MoodAnalysisClient, MoodAnalysisClientSync


async def example_async():
    """Example using async client."""
    print("=== Async Client Example ===\n")
    
    async with MoodAnalysisClient("http://localhost:8000") as client:
        # Check health
        print("1. Checking API health...")
        health = await client.health_check()
        print(f"   Status: {health['status']}\n")
        
        # Get available platforms
        print("2. Getting available platforms...")
        platforms = await client.get_available_platforms()
        print(f"   Platforms: {platforms}\n")
        
        # Get available models
        print("3. Getting available models...")
        models = await client.get_available_models()
        print(f"   Models: {models[:2]}... (showing first 2)\n")
        
        # Start scraping
        print("4. Starting scraping job...")
        job_id = await client.start_scraping(
            scrapper_type="twitter",
            limit=20
        )
        print(f"   Job ID: {job_id}\n")
        
        # Check status
        print("5. Checking scraper status...")
        status = await client.get_scraper_status(job_id)
        print(f"   Status: {status['status']}\n")
        
        # Get latest data (if available)
        try:
            print("6. Getting latest scraped data...")
            data = await client.get_latest_scraped_data()
            print(f"   Total entries: {len(data.get('entries', []))}\n")
        except Exception as e:
            print(f"   (No data yet: {str(e)})\n")
        
        # Start analysis
        print("7. Starting mood analysis...")
        analysis_id = await client.analyze_from_scrapper(
            batch_size=5
        )
        print(f"   Analysis Job ID: {analysis_id}\n")
        
        # Check analysis status
        print("8. Checking analysis status...")
        analysis_status = await client.get_analysis_status(analysis_id)
        print(f"   Status: {analysis_status['status']}")
        print(f"   Entries processed: {analysis_status.get('entries_processed', 0)}\n")


def example_sync():
    """Example using synchronous client."""
    print("\n=== Synchronous Client Example ===\n")
    
    client = MoodAnalysisClientSync("http://localhost:8000")
    
    # Check health
    print("1. Checking API health...")
    health = client.health_check()
    print(f"   Status: {health['status']}\n")
    
    # Run complete pipeline
    print("2. Running complete pipeline (scrape + analyze)...")
    try:
        report = client.run_pipeline(scrapper_type="all")
        print(f"   Overall sentiment: {report.get('overall_sentiment')}")
        print(f"   Total entries: {report.get('total_entries', 0)}\n")
    except Exception as e:
        print(f"   Error: {str(e)}\n")


def example_direct_api_calls():
    """Example with direct HTTP requests."""
    print("\n=== Direct HTTP Request Examples ===\n")
    
    import requests
    
    base_url = "http://localhost:8000"
    
    # Health check
    print("1. Health check:")
    response = requests.get(f"{base_url}/health")
    print(f"   {response.json()}\n")
    
    # Start scraping
    print("2. Start scraping:")
    response = requests.post(
        f"{base_url}/api/v1/scrapper/run",
        json={"scrapper_type": "reddit", "limit": 10}
    )
    print(f"   Job ID: {response.json()['id']}\n")
    
    # Get available models
    print("3. Available models:")
    response = requests.get(f"{base_url}/api/v1/mood/models")
    print(f"   Models: {response.json()['models'][:2]}...\n")


if __name__ == "__main__":
    # Run examples
    print("📊 Mood Analysis API Client Examples\n")
    print("=" * 50 + "\n")
    
    # Run async example
    try:
        asyncio.run(example_async())
    except Exception as e:
        print(f"Error in async example: {str(e)}\n")
    
    # Run sync example
    try:
        example_sync()
    except Exception as e:
        print(f"Error in sync example: {str(e)}\n")
    
    # Run direct API calls example
    try:
        example_direct_api_calls()
    except Exception as e:
        print(f"Error in direct API example: {str(e)}\n")
    
    print("=" * 50)
    print("\n✅ Examples completed!")
    print("\nFor more information, see:")
    print("  - README.md: API documentation")
    print("  - client.py: Client library")
    print("  - tests.py: Integration tests")
