# 🚀 Secure Deployment Guide for HubSpot Dashboard

## 🔒 Security First!

This guide ensures your HubSpot API key is never exposed in your code or repository.

## 📋 Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- HubSpot Private App Access Token

## 🚀 Quick Deployment (Recommended)

### Step 1: Prepare Your Repository

1. **Run the deployment helper**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Create your environment file**:
   ```bash
   cp env.example .env
   # Edit .env and add your actual HubSpot token
   ```

3. **Extract your data** (if not done already):
   ```bash
   python3 simple_hubspot_extractor.py
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy HubSpot dashboard securely"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select the repository and branch
   - **IMPORTANT**: In the "Secrets" section, add:
     ```
     HUBSPOT_ACCESS_TOKEN = your_actual_token_here
     ```
   - Click "Deploy!"

3. **Share with your team**:
   - Copy the generated URL
   - Share with your team members

## 🔧 Manual Setup (Alternative)

### For Team Members (Local Development)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd hubspot
   ```

2. **Set up environment**:
   ```bash
   cp env.example .env
   # Edit .env with your HubSpot token
   pip install -r requirements.txt
   ```

3. **Extract data**:
   ```bash
   python3 simple_hubspot_extractor.py
   ```

4. **Run dashboard**:
   ```bash
   streamlit run simple_deal_dashboard.py
   ```

### For Production Deployment

## Option 1: Streamlit Cloud (Recommended) ✅

**Advantages**: Free, secure, automatic deployments, easy sharing

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "HubSpot dashboard with secure environment variables"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - In the "Secrets" section, add:
     ```
     HUBSPOT_ACCESS_TOKEN = your_hubspot_access_token_here
     ```
   - Deploy!

3. **Share the URL** with your team

## Option 2: Heroku

1. **Create Procfile**:
   ```bash
   echo "web: streamlit run simple_deal_dashboard.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set HUBSPOT_ACCESS_TOKEN=your_token_here
   git push heroku main
   ```

## Option 3: Railway

1. Connect GitHub repository
2. Set environment variable: `HUBSPOT_ACCESS_TOKEN=your_token_here`
3. Deploy automatically

## 🔒 Security Best Practices

### ✅ What's Secure:
- ✅ API key stored in environment variables
- ✅ `.env` file excluded from Git commits
- ✅ `env.example` provides template for other developers
- ✅ Production deployments use platform-specific secret management
- ✅ No hardcoded paths or tokens in code
- ✅ CSV files excluded from repository

### ❌ What to Avoid:
- ❌ Never commit `.env` files
- ❌ Never hardcode API tokens in code
- ❌ Never commit CSV data files
- ❌ Never share API tokens in chat/email

## 📁 Files Overview

- `simple_deal_dashboard.py` - Main dashboard application
- `simple_hubspot_extractor.py` - Data extraction script
- `deploy.sh` - Deployment helper script
- `setup.sh` - Local setup script
- `run_simple_dashboard.sh` - Quick start script
- `env.example` - Environment template (safe to commit)
- `.env` - Your actual API key (NOT committed)
- `.gitignore` - Excludes sensitive files
- `.streamlit/config.toml` - Streamlit configuration

## 🆘 Troubleshooting

### Common Issues:

1. **"No HubSpot deals CSV files found"**
   - Run: `python3 simple_hubspot_extractor.py`
   - Check your `.env` file has the correct token

2. **"HUBSPOT_ACCESS_TOKEN environment variable is required"**
   - Create `.env` file: `cp env.example .env`
   - Add your token to `.env`

3. **Dashboard shows old data**
   - Run the extractor again to get fresh data
   - The dashboard automatically uses the most recent CSV file

4. **Streamlit Cloud deployment fails**
   - Check that your secrets are set correctly
   - Ensure your repository is public or you have Streamlit Cloud Pro

## 🔄 Updating Data

To refresh your dashboard with new data:

1. **Local**: Run `python3 simple_hubspot_extractor.py`
2. **Streamlit Cloud**: The app will automatically use the latest data from your repository

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your HubSpot API token is valid
3. Ensure all dependencies are installed
4. Check the Streamlit Cloud logs for deployment errors
