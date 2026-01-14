#!/bin/bash
#
# pyine CLI Usage Examples
#
# This script demonstrates common CLI commands for interacting with the INE API.
# For more details on any command, run `pyine [COMMAND] --help`.

echo "=========================================="
echo "pyine CLI Examples"
echo "=========================================="

# --- Searching for Indicators ---
echo -e "\n# 1. Search for indicators by keyword"
pyine search "gdp" --limit 5

echo -e "\n# 2. Search for indicators within a specific theme"
pyine search "employment" --theme "Labour market" --limit 5

# --- Getting Indicator Information ---
echo -e "\n# 3. Get detailed information about an indicator"
pyine info 0004167

echo -e "\n# 4. Get information in Portuguese"
pyine info 0004167 --lang PT

# --- Listing Available Metadata ---
echo -e "\n# 5. List all available statistical themes"
pyine list-commands themes

echo -e "\n# 6. List indicators within a theme"
pyine list-commands indicators --theme "Population" --limit 5

echo -e "\n# 7. View available dimensions for an indicator"
pyine dimensions 0004167

# --- Downloading Data ---
echo -e "\n# 8. Download data to a CSV file (default format)"
pyine download 0004167 --output population_data.csv

echo -e "\n# 9. Download data as a JSON file"
pyine download 0004167 --output population_data.json --output-format json

echo -e "\n# 10. Download data with a dimension filter"
pyine download 0004167 --output filtered_population_data.csv --dimension "Dim1=2023"

# --- Cache Management ---
echo -e "\n# 11. View cache information"
pyine cache info

echo -e "\n# 12. Clear the cache (requires confirmation)"
echo "# To run: pyine cache clear --yes"
echo "# (Command is commented out to prevent accidental clearing)"

# --- Help and Version ---
echo -e "\n# 13. Get help for a specific command"
pyine download --help

echo -e "\n# 14. Check the installed version of pyine"
pyine --version

echo -e "\n=========================================="
echo "All CLI examples demonstrated!"
echo "=========================================="