#!/bin/bash
# Quick run script for crypto sentiment scraper

echo
echo "========================================================="
echo "  Crypto Sentiment Data Sourcing - Pipeline Running"
echo "========================================================="
echo

if ! python3 -m data_sourcing.main; then
    echo "✗ Pipeline failed - check logs in data_sourcing/output/"
else
    echo "✓ Pipeline complete! Check data_sourcing/output/ for results."
fi

echo
read -p "Press [Enter] to exit..."
