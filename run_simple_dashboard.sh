#!/bin/bash

# Simple HubSpot Deal Pipeline Dashboard Startup Script

echo "🚀 Starting Simple Deal Pipeline Dashboard..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "hubspot_deals_20250916_160025.csv" ]; then
    echo "❌ Deal data file not found: hubspot_deals_20250916_160025.csv"
    echo "   Please ensure your HubSpot data file is in the current directory"
    exit 1
fi

if [ ! -f "csv_field_mapping.json" ]; then
    echo "❌ Field mapping file not found: csv_field_mapping.json"
    exit 1
fi

# Install requirements if needed
echo "📦 Checking dependencies..."
python3 -c "import streamlit, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing required packages..."
    python3 -m pip install streamlit pandas numpy
fi

# Start the dashboard
echo ""
echo "🌐 Starting Simple Deal Dashboard..."
echo "   Dashboard will be available at: http://localhost:8501"
echo "   This shows deals as rows and weeks as columns"
echo "   Press Ctrl+C to stop the dashboard"
echo ""

python3 -m streamlit run simple_deal_dashboard.py --server.headless false
