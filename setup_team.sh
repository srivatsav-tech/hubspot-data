#!/bin/bash

# Team Setup Script for HubSpot Dashboard
echo "🚀 Setting up HubSpot Dashboard for your team..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env and add your HubSpot API key:"
    echo "   HUBSPOT_ACCESS_TOKEN=your_api_key_here"
    echo ""
    echo "🔑 Get your API key from: HubSpot Account Settings > Integrations > Private Apps"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if data file exists
if [ ! -f "hubspot_deals_20250916_160025.csv" ]; then
    echo "⚠️  Data file not found. Please ensure hubspot_deals_20250916_160025.csv is in this directory."
    exit 1
fi

# Start the dashboard
echo "🌐 Starting dashboard..."
echo "   Dashboard will be available at: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run simple_deal_dashboard.py
