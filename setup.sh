#!/bin/bash

# HubSpot Dashboard Setup Script
echo "🚀 Setting up HubSpot Dashboard..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# HubSpot API Configuration
# This file contains your actual API key and should NEVER be committed to version control

# Your HubSpot Private App Access Token
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token_here
EOF
    echo "✅ Created .env file with your API key"
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if data file exists
if [ ! -f "hubspot_deals_20250916_160025.csv" ]; then
    echo "⚠️  Data file not found. Please ensure hubspot_deals_20250916_160025.csv is in this directory."
    exit 1
fi

echo "🎉 Setup complete! You can now:"
echo "   1. Run the dashboard: ./run_simple_dashboard.sh"
echo "   2. Or run manually: streamlit run simple_deal_dashboard.py"
echo "   3. Dashboard will be available at: http://localhost:8501"
