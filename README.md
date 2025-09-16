# HubSpot Deal Pipeline Dashboard

A flexible, powerful dashboard to track deal pipeline progression over customizable time periods with different frequencies.

**Shows deals as rows and time periods as columns** - perfect for tracking stage progression at any granularity.

## 🚀 Quick Deployment

**Want to deploy this to Streamlit Cloud?** Follow our secure deployment guide:

1. **Quick Deploy**: Run `./deploy.sh` for automated setup
2. **Step-by-Step**: See [STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md)
3. **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## Features

- **🔄 Live Data Refresh**: Pull fresh data directly from HubSpot API with one click
- **Flexible Time Analysis**: Choose any date range with Daily, Weekly, or Monthly frequency
- **Quick Analysis Options**: "Last 13 Weeks" (Weekly) and "Last 12 Months" (Monthly) presets
- **Stage Change Detection**: Identify when deals moved between pipeline stages
- **Interactive Filtering**: Filter deals by creation date, stage, and deal name
- **Visual Analytics**: Multiple chart types including funnel charts, timeline views, and distribution charts
- **Export Functionality**: Download filtered data and analysis results
- **🔒 Secure**: API keys stored in environment variables, never exposed in code

## Files Overview

- `simple_hubspot_extractor.py` - Script to extract deal data from HubSpot API
- `simple_deal_dashboard.py` - **Main dashboard** (deals as rows, weeks as columns)
- `deploy.sh` - Automated deployment helper script
- `requirements.txt` - Python dependencies
- `env.example` - Environment template (safe to commit)
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `STEP_BY_STEP_DEPLOYMENT.md` - Detailed step-by-step instructions

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** (REQUIRED for security):
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your HubSpot API key
   # Get your API key from: HubSpot Account Settings > Integrations > Private Apps
   HUBSPOT_ACCESS_TOKEN=your_actual_api_key_here
   ```

3. **Extract your data**:
   ```bash
   python3 simple_hubspot_extractor.py
   ```

## Security Setup

**⚠️ IMPORTANT**: Never commit your `.env` file or hardcode API keys in your source code!

1. **Create a `.env` file** from the provided `env.example`
2. **Add your HubSpot API key** to the `.env` file
3. **Add `.env` to your `.gitignore`** to prevent accidental commits
4. **Revoke and regenerate** your API key if it was ever exposed in code

The scripts now use environment variables for secure API key handling.

## Usage

### Running the Dashboard

**Quick start:**
```bash
./run_simple_dashboard.sh
```

**Manual start:**
```bash
streamlit run simple_deal_dashboard.py
```

The dashboard will be available at `http://localhost:8501` in your browser.

### 🔄 Data Refresh Feature

The dashboard now includes a **"Refresh Data"** button in the top-right corner that allows you to:

- **Pull fresh data** directly from HubSpot API without running external scripts
- **Automatically update** the dashboard with the latest deal information
- **See real-time progress** with progress bars and status updates
- **Handle errors gracefully** with clear error messages

**How to use:**
1. Click the "🔄 Refresh Data" button in the top-right corner
2. Watch the progress as data is fetched from HubSpot
3. The dashboard will automatically reload with fresh data

**Requirements:**
- Your `HUBSPOT_ACCESS_TOKEN` must be set in the environment variables
- The dashboard will automatically use the most recent CSV file after refresh

### Dashboard Features

#### Filters (Sidebar)
- **Creation Date Range**: Filter deals by when they were created
- **Stage Filter**: Include/exclude specific pipeline stages
- **Deal Name Filter**: Focus on specific deals (optional)

#### Main Dashboard Sections

1. **Key Metrics**: Total deals, weeks analyzed, stage changes, and latest week activity

2. **Visualizations**:
   - **Pipeline Funnel**: Shows deal progression through stages for selected week
   - **Stage Distribution**: Stacked bar chart showing stage distribution over time
   - **Stage Changes Timeline**: Line chart showing when deals changed stages
   - **Deal Velocity**: Average time spent in each stage

3. **Data Tables**:
   - **Weekly Snapshots**: All deal-stage combinations by week
   - **Stage Changes**: Detailed log of when deals moved between stages
   - **Summary**: Key statistics and conversion funnel data

4. **Export Options**: Download filtered data as CSV or summary as JSON

### Running the Analysis Script Directly

You can also run the analysis script independently:

```bash
python3 simple_hubspot_extractor.py
```

This will generate a timestamped CSV file with your HubSpot data.

## Pipeline Stages

The dashboard tracks the following pipeline stages:

### Positive Progression Stages
- **Sign-up**: Initial sign-up stage
- **Outreach done**: Outreach activities completed
- **Demo Booked**: Demo appointment scheduled
- **Demo Done**: Demo presentation completed
- **Customer Converted**: Customer successfully converted
- **Closed Won**: Deal closed and won

### Negative/Exit Stages
- **Junk**: Deal marked as junk
- **Not a good fit**: Deal not suitable
- **Closed Lost**: Deal closed and lost
- **Churned**: Customer churned

### Follow-up Stages
- **Post-demo follow-up**: Follow-up after demo
- **Follow-up done**: Follow-up activities completed
- **$$$$ follow-ups**: High-value follow-ups
- **Active trial $$$$ #haisha**: Active trial stage

## Data Structure

### Weekly Snapshots
Each row represents a deal in a specific week:
- `week_start`: Start date of the week
- `week_end`: End date of the week
- `deal_id`: Unique deal identifier
- `deal_name`: Human-readable deal name
- `created_at`: When the deal was created
- `stage`: Stage the deal was in during this week
- `stage_entered_date`: When the deal entered this stage

### Stage Changes
Each row represents a detected stage change:
- `deal_id`: Unique deal identifier
- `deal_name`: Human-readable deal name
- `week_start`: Week when change occurred
- `previous_stage`: Stage before the change
- `current_stage`: Stage after the change
- `stage_change_date`: Exact date of the change

## Customization

### Adding New Stages
To add new pipeline stages:

1. Update the `stage_mapping` dictionary in `simple_deal_dashboard.py`
2. Add the corresponding API field mapping
3. Update the `csv_field_mapping.json` file

### Modifying Analysis Period
Change the `weeks_back` parameter in the `run_analysis()` method to analyze different time periods.

### Custom Visualizations
Add new chart types by creating new functions in `simple_deal_dashboard.py` following the existing pattern.

## Troubleshooting

### Common Issues

1. **"No data available"**: Check that your CSV file exists and has the expected column structure
2. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **Empty charts**: Verify that your data contains deals within the selected date range and stage filters
4. **"No HubSpot deals CSV files found"**: Use the "🔄 Refresh Data" button to extract data from HubSpot API
5. **"HUBSPOT_ACCESS_TOKEN environment variable is required"**: Set your API token in the `.env` file
6. **Refresh button not working**: Verify your HubSpot API token is valid and has proper permissions

### Data Quality Checks

The analyzer includes built-in data quality checks:
- Handles missing or invalid dates gracefully
- Filters out deals with no stage progression
- Provides warnings for unusual data patterns

## Performance Notes

- The analysis processes all deals and generates weekly snapshots, which can be memory-intensive for large datasets
- Consider filtering by date range for very large datasets
- The dashboard caches analysis results for better performance during interactive use

## Support

For issues or questions:
1. Check the console output for error messages
2. Verify your data files are in the correct format
3. Ensure all dependencies are properly installed
4. See the deployment guides for deployment-specific issues
