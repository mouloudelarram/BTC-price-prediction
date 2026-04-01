#!/usr/bin/env python3
"""Test script to trace analyzer flow."""

import sys
import asyncio
from market_mood_analyzer import MoodAnalyzer
import config

async def main():
    analyzer = MoodAnalyzer(config)
    
    # Load data
    raw_entries = analyzer.data_loader.load_all()
    print(f"\n[OK] Raw entries loaded: {len(raw_entries)}")
    
    # Preprocess
    entries_to_process = []
    skip_count = 0
    for idx, entry in enumerate(raw_entries):
        preprocessed = analyzer.data_loader.preprocess(entry)
        if preprocessed:
            entry_id = analyzer.data_loader.generate_entry_id(preprocessed)
            
            # Check checkpoint
            if analyzer.progress_tracker.is_processed(entry_id):
                skip_count += 1
                continue
            
            entries_to_process.append((entry_id, preprocessed))
        
        if idx < 3:
            print(f"\nEntry {idx}:")
            print(f"  preprocessed={preprocessed is not None}")
            if preprocessed:
                print(f"  text_len={len(preprocessed['text'])}")
    
    print(f"\n[OK] Preprocessed entries: {len(entries_to_process)}")
    print(f"[OK] Skipped (checkpoint): {skip_count}")
    print(f"[OK] Total to process: {len(entries_to_process)}")
    
    # Check checkpoint stats
    stats = analyzer.progress_tracker.get_stats()
    print(f"\nCheckpoint stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
