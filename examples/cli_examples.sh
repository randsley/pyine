#!/bin/bash

# CLI Usage Examples for pyine
# This script demonstrates various CLI commands

echo "=========================================="
echo "pyine CLI Examples"
echo "=========================================="

echo ""
echo "Example 1: Search for indicators"
echo "------------------------------------------"
pyine search "gdp"

echo ""
echo "Example 2: Search with filters"
echo "------------------------------------------"
pyine search "population" --theme "Population" --limit 5

echo ""
echo "Example 3: Get indicator information"
echo "------------------------------------------"
pyine info 0004167

echo ""
echo "Example 4: Get indicator information in Portuguese"
echo "------------------------------------------"
pyine info 0004167 --lang PT

echo ""
echo "Example 5: List all themes"
echo "------------------------------------------"
pyine list themes

echo ""
echo "Example 6: List indicators in a theme"
echo "------------------------------------------"
pyine list indicators --theme "Population" --limit 10

echo ""
echo "Example 7: View available dimensions"
echo "------------------------------------------"
pyine dimensions 0004167

echo ""
echo "Example 8: Download data as CSV"
echo "------------------------------------------"
pyine download 0004167 --output population.csv

echo ""
echo "Example 9: Download data as JSON"
echo "------------------------------------------"
pyine download 0004167 --output population.json --format json

echo ""
echo "Example 10: Download with dimension filters"
echo "------------------------------------------"
pyine download 0004167 --output filtered.csv --dimension "Dim1=2023"

echo ""
echo "Example 11: Download without metadata"
echo "------------------------------------------"
pyine download 0004167 --output data_only.csv --no-metadata

echo ""
echo "Example 12: View cache information"
echo "------------------------------------------"
pyine cache info

echo ""
echo "Example 13: Clear cache (with confirmation)"
echo "------------------------------------------"
echo "# pyine cache clear"
echo "# (Commented out to prevent accidental cache clearing)"

echo ""
echo "Example 14: Get help for any command"
echo "------------------------------------------"
pyine search --help

echo ""
echo "Example 15: Check version"
echo "------------------------------------------"
pyine --version

echo ""
echo "=========================================="
echo "All CLI examples demonstrated!"
echo "=========================================="
