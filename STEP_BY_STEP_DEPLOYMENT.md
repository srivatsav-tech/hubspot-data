# 🚀 Step-by-Step Deployment Guide

## Prerequisites Checklist

Before starting, make sure you have:
- [ ] GitHub account
- [ ] Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- [ ] HubSpot Private App Access Token
- [ ] Git installed on your computer

## Step 1: Prepare Your Local Environment

### 1.1 Create Environment File
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your HubSpot token
# Replace 'your_hubspot_access_token_here' with your actual token
```

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.3 Extract Your Data
```bash
python3 simple_hubspot_extractor.py
```

This will create a CSV file with your HubSpot data.

### 1.4 Test Locally (Optional)
```bash
streamlit run simple_deal_dashboard.py
```

Visit `http://localhost:8501` to verify everything works.

## Step 2: Prepare Git Repository

### 2.1 Initialize Git (if not already done)
```bash
git init
```

### 2.2 Add Files to Git
```bash
git add .
git commit -m "Initial commit: HubSpot dashboard"
```

### 2.3 Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it (e.g., "hubspot-dashboard")
4. Make it **Public** (required for free Streamlit Cloud)
5. Don't initialize with README (you already have files)
6. Click "Create repository"

### 2.4 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Streamlit Cloud

### 3.1 Go to Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 3.2 Configure Your App
1. **Repository**: Select your GitHub repository
2. **Branch**: Select `main`
3. **Main file path**: `simple_deal_dashboard.py`
4. **App URL**: Choose a custom URL (optional)

### 3.3 Add Secrets (CRITICAL!)
1. Click "Advanced settings"
2. In the "Secrets" section, add:
   ```
   HUBSPOT_ACCESS_TOKEN = your_actual_hubspot_token_here
   ```
   ⚠️ **Important**: Replace `your_actual_hubspot_token_here` with your real token!

### 3.4 Deploy
1. Click "Deploy!"
2. Wait for deployment to complete (2-3 minutes)
3. Your app will be available at the provided URL

## Step 4: Verify Deployment

### 4.1 Check Your App
1. Visit your Streamlit Cloud URL
2. Verify the dashboard loads correctly
3. Check that data is displayed properly

### 4.2 Test Data Refresh
1. Run the extractor locally: `python3 simple_hubspot_extractor.py`
2. Commit and push the new CSV file:
   ```bash
   git add hubspot_deals_*.csv
   git commit -m "Update data"
   git push origin main
   ```
3. Streamlit Cloud will automatically redeploy with new data

## Step 5: Share with Your Team

### 5.1 Share the URL
- Copy your Streamlit Cloud URL
- Share it with your team members
- No additional setup required for viewers

### 5.2 For Team Members Who Need to Update Data
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. Set up environment:
   ```bash
   cp env.example .env
   # Edit .env with their HubSpot token
   pip install -r requirements.txt
   ```

3. Update data and push:
   ```bash
   python3 simple_hubspot_extractor.py
   git add hubspot_deals_*.csv
   git commit -m "Update data"
   git push origin main
   ```

## 🔒 Security Verification

After deployment, verify these security measures:

- [ ] ✅ `.env` file is NOT in your GitHub repository
- [ ] ✅ Your API token is only in Streamlit Cloud secrets
- [ ] ✅ CSV files are in `.gitignore` (they'll be committed for data sharing)
- [ ] ✅ No hardcoded tokens in your code

## 🆘 Troubleshooting

### Common Issues:

**"No HubSpot deals CSV files found"**
- Solution: Run `python3 simple_hubspot_extractor.py` locally and push the CSV file

**"HUBSPOT_ACCESS_TOKEN environment variable is required"**
- Solution: Check that you added the secret correctly in Streamlit Cloud

**App fails to deploy**
- Solution: Check Streamlit Cloud logs, ensure repository is public

**Dashboard shows old data**
- Solution: Run extractor locally and push new CSV file

## 🎉 Success!

Your HubSpot dashboard is now securely deployed and accessible to your team!

**Next Steps:**
- Bookmark your Streamlit Cloud URL
- Set up a schedule to refresh data regularly
- Share the URL with your team
- Consider setting up automated data extraction

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the Streamlit Cloud logs
3. Verify your HubSpot API token is valid
4. Ensure all dependencies are installed correctly
