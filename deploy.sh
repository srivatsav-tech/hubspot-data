#!/bin/bash

# HubSpot Dashboard Deployment Script
# This script helps deploy the HubSpot dashboard to Streamlit Cloud

set -e

echo "🚀 HubSpot Dashboard Deployment Helper"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: HubSpot dashboard"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create a .env file with your HubSpot API token:"
    echo "   HUBSPOT_ACCESS_TOKEN=your_token_here"
    echo ""
    echo "💡 You can copy from env.example:"
    echo "   cp env.example .env"
    echo "   # Then edit .env with your actual token"
    echo ""
    read -p "Press Enter to continue after creating .env file..."
fi

# Check if .env is in .gitignore
if ! grep -q "\.env" .gitignore; then
    echo "🔒 Adding .env to .gitignore for security..."
    echo ".env" >> .gitignore
fi

# Check if CSV files exist
csv_files=$(ls hubspot_deals_*.csv 2>/dev/null | wc -l)
if [ $csv_files -eq 0 ]; then
    echo "📊 No CSV data files found. Running data extraction..."
    echo "💡 Make sure your .env file has the correct HUBSPOT_ACCESS_TOKEN"
    python3 simple_hubspot_extractor.py
else
    echo "✅ Found $csv_files CSV data file(s)"
fi

echo ""
echo "🎯 Ready for deployment! Next steps:"
echo ""
echo "1. 📤 Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Deploy HubSpot dashboard'"
echo "   git push origin main"
echo ""
echo "2. 🌐 Deploy to Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io"
echo "   - Connect your GitHub repository"
echo "   - Add your HUBSPOT_ACCESS_TOKEN in the Secrets section"
echo "   - Deploy!"
echo ""
echo "3. 🔗 Share the URL with your team"
echo ""
echo "🔒 Security reminder: Never commit your .env file!"
echo "   Your API token will be stored securely in Streamlit Cloud secrets."
