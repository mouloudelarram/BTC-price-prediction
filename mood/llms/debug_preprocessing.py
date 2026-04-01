#!/usr/bin/env python3
"""Debug script to identify why entries are being filtered."""

import json
from pathlib import Path
from market_mood_analyzer import DataLoader
import config

data_loader = DataLoader(config.DATA_DIR)

# Load all raw entries
raw_entries = data_loader.load_all()
print(f"✓ Loaded {len(raw_entries)} total raw entries")
print(f"\nREQUIRED_ENTRY_FIELDS: {config.REQUIRED_ENTRY_FIELDS}")

# Sample first few entries to see structure
if raw_entries:
    print(f"\n--- Sample entry structure ---")
    sample = raw_entries[0]
    print(f"Keys: {list(sample.keys())}")
    print(f"Full sample:\n{json.dumps(sample, indent=2)[:500]}")

# Test preprocessing
processed_count = 0
filtered_reasons = {
    "missing_fields": 0,
    "no_text": 0,
    "text_too_short": 0,
    "text_too_long": 0,
    "success": 0,
}

for i, entry in enumerate(raw_entries):
    # Check required fields
    if not all(field in entry for field in config.REQUIRED_ENTRY_FIELDS):
        filtered_reasons["missing_fields"] += 1
        if i < 3:
            missing = [f for f in config.REQUIRED_ENTRY_FIELDS if f not in entry]
            print(f"Entry {i}: Missing fields {missing}")
        continue
    
    # Check text field
    text = entry.get("text") or entry.get("content")
    if not text:
        filtered_reasons["no_text"] += 1
        if i < 3:
            print(f"Entry {i}: No text or content field")
        continue
    
    if not isinstance(text, str):
        filtered_reasons["no_text"] += 1
        if i < 3:
            print(f"Entry {i}: text/content is not a string, type={type(text)}")
        continue
    
    text = text.strip()
    
    # Check length
    if len(text) < config.TEXT_MIN_LENGTH:
        filtered_reasons["text_too_short"] += 1
        if i < 3:
            print(f"Entry {i}: Text too short ({len(text)} chars, min={config.TEXT_MIN_LENGTH})")
        continue
    
    if len(text) > config.TEXT_MAX_LENGTH:
        filtered_reasons["text_too_long"] += 1
        if i < 3:
            print(f"Entry {i}: Text too long ({len(text)} chars, max={config.TEXT_MAX_LENGTH})")
        continue
    
    # If we got here, preprocessing would succeed
    filtered_reasons["success"] += 1
    processed_count += 1

print(f"\n--- Preprocessing Results ---")
print(f"Total entries: {len(raw_entries)}")
for reason, count in filtered_reasons.items():
    pct = (count / len(raw_entries) * 100) if raw_entries else 0
    print(f"  {reason:20}: {count:4} ({pct:5.1f}%)")

print(f"\nWould process: {processed_count} entries")
