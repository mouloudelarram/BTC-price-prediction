"""
Example 1: Basic Usage - Run all scrapers
"""

import asyncio
from data_sourcing.main import main

if __name__ == "__main__":
    async def run():
        await main()
    
    asyncio.run(run())
