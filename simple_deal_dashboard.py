#!/usr/bin/env python3
"""
Simple HubSpot Deal Pipeline Dashboard

Shows deals as rows and weeks as columns, with each cell displaying
the stage for that deal in that week.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
import csv
import time
import os
import glob
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Simple Deal Pipeline Dashboard",
    page_icon="📊",
    layout="wide"
)

class HubSpotExtractor:
    """HubSpot API client for extracting deal data"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_properties_to_extract(self) -> List[str]:
        """Get the properties to extract"""
        return [
            "dealname",
            "hs_v2_date_entered_current_stage",
            "hs_v2_date_entered_1091569281",
            "hs_v2_date_entered_202676095",
            "hs_v2_date_entered_appointmentscheduled",
            "hs_v2_date_entered_1053523303",
            "hs_v2_date_entered_qualifiedtobuy",
            "hs_v2_date_entered_presentationscheduled",
            "hs_v2_date_entered_contractsent",
            "hs_v2_date_entered_981662285",
            "hs_v2_date_entered_1141834547",
            "hs_v2_date_entered_1053523302",
            "hs_v2_date_entered_1120008054",
            "hs_v2_date_entered_closedwon",
            "hs_v2_date_entered_999971918",
            "hs_v2_date_entered_closedlost",
            "hs_v2_date_entered_202676096",
            "hs_v2_date_entered_1053523301",
            "hs_v2_date_entered_1155516059",
            "hs_v2_date_entered_1158033067",
            "hs_v2_date_entered_1053507879",
            "hs_v2_date_entered_1155410330",
            "hs_deal_stage_probability",
            "hs_deal_amount",
            "hubspot_owner_id"
        ]
    
    
    def get_contact_properties(self, contact_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get contact properties including lemlist campaign for given contact IDs"""
        if not contact_ids:
            return {}
        
        contacts_data = {}
        
        # Process contacts in batches to avoid API limits
        batch_size = 100
        for i in range(0, len(contact_ids), batch_size):
            batch_ids = contact_ids[i:i + batch_size]
            
            try:
                url = f"{self.base_url}/crm/v3/objects/contacts/batch/read"
                payload = {
                    "properties": ["firstname", "lastname", "email", "lemlistlmlstcampaign"],
                    "inputs": [{"id": contact_id} for contact_id in batch_ids]
                }
                
                response = requests.post(url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    for result in data.get("results", []):
                        contact_id = result.get("id")
                        properties = result.get("properties", {})
                        contacts_data[contact_id] = {
                            "firstname": properties.get("firstname", ""),
                            "lastname": properties.get("lastname", ""),
                            "email": properties.get("email", ""),
                            "lemlist_campaign": properties.get("lemlistlmlstcampaign", ""),
                            "full_name": f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip()
                        }
                else:
                    st.warning(f"Failed to fetch contact properties: {response.status_code}")
                    
            except Exception as e:
                st.warning(f"Error fetching contact properties: {str(e)}")
        
        return contacts_data
    
    def get_all_deals(self, properties: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve all deals with specified properties and associated contacts using optimized batch approach"""
        all_deals = []
        after = None
        page = 1
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Fetch all deals with associations in a single request
        status_text.text("Fetching deals with contact associations...")
        
        while True:
            try:
                url = f"{self.base_url}/crm/v3/objects/deals"
                params = {
                    "properties": ",".join(properties),
                    "associations": "contacts",  # This gets contact associations in the same request!
                    "limit": limit
                }
                
                if after:
                    params["after"] = after
                
                status_text.text(f"Fetching page {page}...")
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    deals = data.get("results", [])
                    all_deals.extend(deals)
                    
                    # Update progress
                    progress_bar.progress(min(page * 0.2, 0.4))
                    
                    # Check if there are more pages
                    paging = data.get("paging", {})
                    after = paging.get("next", {}).get("after")
                    
                    if not after:
                        break
                    
                    page += 1
                    time.sleep(0.1)  # Rate limiting
                    
                else:
                    st.error(f"Error fetching deals: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    break
                    
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
                break
        
        progress_bar.progress(0.4)
        status_text.text(f"Retrieved {len(all_deals)} deals, extracting contact IDs...")
        
        # Step 2: Extract all unique contact IDs from associations
        all_contact_ids = set()
        deal_contact_mapping = {}
        
        for deal in all_deals:
            deal_id = deal.get("id")
            associations = deal.get("associations", {})
            contact_associations = associations.get("contacts", {}).get("results", [])
            
            contact_ids = []
            for assoc in contact_associations:
                contact_id = assoc.get("id")
                if contact_id:
                    contact_ids.append(str(contact_id))
                    all_contact_ids.add(str(contact_id))
            
            deal_contact_mapping[deal_id] = contact_ids
        
        progress_bar.progress(0.6)
        status_text.text(f"Found {len(all_contact_ids)} unique contacts, fetching properties...")
        
        # Step 3: Batch fetch contact properties
        contacts_data = self.get_contact_properties(list(all_contact_ids))
        
        progress_bar.progress(0.8)
        status_text.text("Adding contact information to deals...")
        
        # Step 4: Add contact information to deals
        for deal in all_deals:
            deal_id = deal.get("id")
            associated_contacts = deal_contact_mapping.get(deal_id, [])
            
            # Get the last contact (most recent association)
            last_contact = None
            last_lemlist_campaign = ""
            
            if associated_contacts:
                # Get the last contact ID (assuming they're ordered by association date)
                last_contact_id = associated_contacts[-1]
                last_contact_data = contacts_data.get(last_contact_id, {})
                last_contact = last_contact_data.get("full_name", "")
                last_lemlist_campaign = last_contact_data.get("lemlist_campaign", "")
            
            # Add contact information to deal properties
            deal["properties"]["last_contact_name"] = last_contact or ""
            deal["properties"]["last_contact_lemlist_campaign"] = last_lemlist_campaign or ""
        
        progress_bar.progress(1.0)
        status_text.text(f"Retrieved {len(all_deals)} deals with contact associations")
        
        return all_deals
    
    def export_to_csv(self, deals: List[Dict[str, Any]], output_file: str):
        """Export deals to CSV file"""
        if not deals:
            st.warning("No deals to export")
            return
        
        target_properties = self.get_properties_to_extract()
        # Add the new contact fields to the export
        contact_fields = ["last_contact_name", "last_contact_lemlist_campaign"]
        fieldnames = ["deal_id", "created_at", "updated_at"] + target_properties + contact_fields
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for deal in deals:
                    row = {
                        "deal_id": deal.get("id"),
                        "created_at": deal.get("createdAt"),
                        "updated_at": deal.get("updatedAt")
                    }
                    
                    properties = deal.get("properties", {})
                    for prop in target_properties:
                        row[prop] = properties.get(prop, "")
                    
                    # Add contact information
                    for contact_field in contact_fields:
                        row[contact_field] = properties.get(contact_field, "")
                    
                    writer.writerow(row)
            
            st.success(f"Successfully exported {len(deals)} deals to {output_file}")
            
        except Exception as e:
            st.error(f"Error exporting to CSV: {str(e)}")
    
    def refresh_data(self) -> str:
        """Refresh data from HubSpot API"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"hubspot_deals_{timestamp}.csv"
        
        properties = self.get_properties_to_extract()
        deals = self.get_all_deals(properties)
        
        if deals:
            self.export_to_csv(deals, output_file)
            return output_file
        else:
            st.error("No deals found or error occurred during extraction")
            return None

def robust_date_parser(date_series):
    """Robust date parser that handles multiple ISO datetime formats"""
    def parse_single_date(date_str):
        if pd.isna(date_str) or date_str == '':
            return pd.NaT
        
        try:
            # First try: standard pandas parsing
            return pd.to_datetime(date_str)
        except:
            try:
                # Second try: handle dates without milliseconds
                # Format: 2025-06-11T01:44:00Z
                if isinstance(date_str, str) and 'T' in date_str and 'Z' in date_str and '.' not in date_str:
                    # Add milliseconds if missing
                    if date_str.endswith('Z'):
                        date_str_with_ms = date_str[:-1] + '.000Z'
                        return pd.to_datetime(date_str_with_ms)
                
                # Third try: handle other ISO formats
                return pd.to_datetime(date_str, format='ISO8601')
            except:
                try:
                    # Fourth try: manual parsing for specific format
                    if isinstance(date_str, str) and len(date_str) == 20 and date_str.endswith('Z'):
                        # Format: YYYY-MM-DDTHH:MM:SSZ
                        return pd.to_datetime(date_str, format='%Y-%m-%dT%H:%M:%SZ')
                except:
                    pass
        
        return pd.NaT
    
    return date_series.apply(parse_single_date)

@st.cache_data
def load_and_process_data():
    """Load and process the deal data"""
    try:
        # Look for CSV files in the current directory
        csv_files = glob.glob("hubspot_deals_*.csv")
        if not csv_files:
            st.error("No HubSpot deals CSV files found. Please use the refresh button to extract data from HubSpot.")
            return None
        
        # Use the most recent file
        latest_file = max(csv_files, key=os.path.getctime)
        
        # Get file modification time to show when data was last refreshed
        file_mtime = os.path.getmtime(latest_file)
        last_refreshed = datetime.fromtimestamp(file_mtime)
        
        # Show when data was last refreshed instead of file name
        st.info(f"📊 Data last refreshed from HubSpot: {last_refreshed.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load the CSV data
        df = pd.read_csv(latest_file)
        
        # Convert date columns to datetime using robust parser
        date_columns = [col for col in df.columns if 'date_entered' in col or col in ['created_at', 'updated_at']]
        for col in date_columns:
            df[col] = robust_date_parser(df[col])
        
        # Handle campaign column data types
        if 'last_contact_lemlist_campaign' in df.columns:
            df['last_contact_lemlist_campaign'] = df['last_contact_lemlist_campaign'].fillna('').astype(str)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def refresh_data_from_hubspot():
    """Refresh data from HubSpot API"""
    # Get the access token from environment
    access_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    if not access_token:
        st.error("HUBSPOT_ACCESS_TOKEN environment variable is required. Please set it in your .env file.")
        return False
    
    try:
        # Initialize extractor
        extractor = HubSpotExtractor(access_token)
        
        # Refresh data
        with st.spinner("Refreshing data from HubSpot..."):
            output_file = extractor.refresh_data()
            
        if output_file:
            # Clear the cache to force reload
            load_and_process_data.clear()
            st.success("Data refreshed successfully!")
            st.rerun()
            return True
        else:
            return False
            
    except Exception as e:
        st.error(f"Error refreshing data: {str(e)}")
        return False

def get_deal_stage_progression(row):
    """Get the chronological progression of stages for a deal"""
    stage_dates = []
    stage_mapping = {
        # Initial/Entry Stages
        'hs_v2_date_entered_1091569281': 'Sign-up',
        'hs_v2_date_entered_1053523303': 'Outreach done',
        'hs_v2_date_entered_1053523302': 'To reach out',
        
        # Demo/Qualification Stages
        'hs_v2_date_entered_qualifiedtobuy': 'Demo Booked',
        'hs_v2_date_entered_presentationscheduled': 'Demo Done',
        'hs_v2_date_entered_appointmentscheduled': 'Relevant Reply',
        
        # Conversion Stages
        'hs_v2_date_entered_contractsent': 'Customer Converted',
        'hs_v2_date_entered_closedwon': 'Closed Won',
        
        # Follow-up Stages
        'hs_v2_date_entered_1141834547': 'Post-demo follow-up',
        'hs_v2_date_entered_1053523301': 'Follow-up done',
        'hs_v2_date_entered_1158033067': '$$$$ follow-ups',
        
        # Active Trial Stage
        'hs_v2_date_entered_1155410330': 'Active trial $$$$ #haisha',
        
        # Negative/Rejection Stages
        'hs_v2_date_entered_202676095': 'Junk',
        'hs_v2_date_entered_981662285': 'Not a good fit',
        'hs_v2_date_entered_closedlost': 'Closed Lost',
        'hs_v2_date_entered_1053507879': 'Churned',
        'hs_v2_date_entered_1155516059': 'PoC not right but company relevant',
        'hs_v2_date_entered_1120008054': 'Timing not right',
        
        # No Show Stage
        'hs_v2_date_entered_202676096': 'No Show',
        
        # Cold Call Stage
        'hs_v2_date_entered_999971918': 'Cold call done'
    }
    
    for field, stage_name in stage_mapping.items():
        if field in row and pd.notna(row[field]):
            stage_dates.append((stage_name, row[field]))
    
    # Sort by date
    stage_dates.sort(key=lambda x: x[1])
    return stage_dates

def create_period_matrix(df, start_date, end_date, frequency):
    """Create a matrix of deals vs periods showing stages"""
    from datetime import timezone
    
    # Ensure dates are timezone-aware
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    
    # Generate period dates based on frequency (oldest periods first)
    period_dates = []
    current_date = start_date
    
    if frequency == 'Daily':
        while current_date <= end_date:
            period_dates.append(current_date)
            current_date += timedelta(days=1)
    elif frequency == 'Weekly':
        while current_date <= end_date:
            period_dates.append(current_date)
            current_date += timedelta(weeks=1)
    elif frequency == 'Monthly':
        while current_date <= end_date:
            period_dates.append(current_date)
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    # Create matrix data
    matrix_data = []
    
    for _, deal in df.iterrows():
        # Get deal progression
        progression = get_deal_stage_progression(deal)
        
        # Create row for this deal
        deal_id = deal['deal_id']
        deal_name = deal['dealname']
        
        deal_row = {
            'Deal Name': deal_name,
            'Deal ID': deal_id,  # Keep Deal ID in backend for HubSpot links
            'Created': deal['created_at'].strftime('%Y-%m-%d') if pd.notna(deal['created_at']) else 'Unknown',
            'Lemlist Campaign': deal.get('last_contact_lemlist_campaign', '')
        }
        
        # For each period, find what stage the deal was in
        for period_date in period_dates:
            if frequency == 'Daily':
                period_end = period_date + timedelta(days=1)
                period_key = period_date.strftime('%Y-%m-%d')
            elif frequency == 'Weekly':
                period_end = period_date + timedelta(weeks=1)
                period_key = period_date.strftime('%Y-%m-%d')
            elif frequency == 'Monthly':
                # Calculate end of month
                if period_date.month == 12:
                    period_end = period_date.replace(year=period_date.year + 1, month=1)
                else:
                    period_end = period_date.replace(month=period_date.month + 1)
                period_key = period_date.strftime('%Y-%m')
            
            # Skip if deal was created after this period (only if created_at is not NaN)
            if pd.notna(deal['created_at']) and deal['created_at'] > period_end:
                deal_row[period_key] = ''
                continue
            
            # Find stage during this period
            stage_during_period = ''
            for stage_name, stage_date in progression:
                if stage_date and stage_date <= period_end:
                    stage_during_period = stage_name
                else:
                    break
            
            deal_row[period_key] = stage_during_period
        
        matrix_data.append(deal_row)
    
    return pd.DataFrame(matrix_data), period_dates

def calculate_stagnant_deals(matrix_df, period_dates, frequency):
    """Calculate deals that haven't changed stage for n periods"""
    stagnant_deals = []
    period_columns = [col for col in matrix_df.columns if col not in ['Deal Name', 'Deal ID', 'Created', 'Lemlist Campaign']]
    
    for _, row in matrix_df.iterrows():
        stages = [stage for stage in row[period_columns] if stage]
        if len(stages) > 0:
            # Find the last stage change
            last_stage = stages[-1]
            stagnant_periods = 0
            
            # Count consecutive periods with the same stage from the end
            for i in range(len(stages) - 1, -1, -1):
                if stages[i] == last_stage:
                    stagnant_periods += 1
                else:
                    break
            
            stagnant_deals.append({
                'deal_name': row['Deal Name'],
                'deal_id': row['Deal ID'],
                'current_stage': last_stage,
                'stagnant_periods': stagnant_periods,
                'total_periods': len([s for s in stages if s])
            })
    
    return pd.DataFrame(stagnant_deals)

def style_cell(value):
    """Style individual cells with better colors and black text"""
    if value == '':
        return 'background-color: #f8f9fa; color: #000000; border: 1px solid #dee2e6'
    
    # Better color scheme with black text for visibility
    # Organized by stage type: Entry/Initial (blue), Demo/Qualification (orange), Conversion (green), Follow-up (purple), Negative (red), Neutral (gray)
    stage_colors = {
        # Entry/Initial Stages (Blue tones)
        'Sign-up': 'background-color: #e3f2fd; color: #000000; border: 1px solid #dee2e6',
        'To reach out': 'background-color: #e1f5fe; color: #000000; border: 1px solid #dee2e6',
        'Outreach done': 'background-color: #e8eaf6; color: #000000; border: 1px solid #dee2e6',
        
        # Demo/Qualification Stages (Orange/Yellow tones)
        'Demo Booked': 'background-color: #fff3e0; color: #000000; border: 1px solid #dee2e6',
        'Demo Done': 'background-color: #fff8e1; color: #000000; border: 1px solid #dee2e6',
        'Relevant Reply': 'background-color: #f3e5f5; color: #000000; border: 1px solid #dee2e6',
        
        # Conversion Stages (Green tones)
        'Customer Converted': 'background-color: #e8f5e8; color: #000000; border: 1px solid #dee2e6',
        'Closed Won': 'background-color: #c8e6c9; color: #000000; border: 1px solid #dee2e6',
        'Active trial $$$$ #haisha': 'background-color: #a5d6a7; color: #000000; border: 1px solid #dee2e6',
        
        # Follow-up Stages (Purple/Pink tones)
        'Post-demo follow-up': 'background-color: #fce4ec; color: #000000; border: 1px solid #dee2e6',
        'Follow-up done': 'background-color: #f8bbd9; color: #000000; border: 1px solid #dee2e6',
        '$$$$ follow-ups': 'background-color: #e1bee7; color: #000000; border: 1px solid #dee2e6',
        
        # Negative/Rejection Stages (Red tones)
        'Closed Lost': 'background-color: #ffcdd2; color: #000000; border: 1px solid #dee2e6',
        'Churned': 'background-color: #ffcdd2; color: #000000; border: 1px solid #dee2e6',
        'Not a good fit': 'background-color: #ffebee; color: #000000; border: 1px solid #dee2e6',
        'PoC not right but company relevant': 'background-color: #ffcdd2; color: #000000; border: 1px solid #dee2e6',
        
        # Neutral/Other Stages (Gray tones)
        'Junk': 'background-color: #f5f5f5; color: #000000; border: 1px solid #dee2e6',
        'No Show': 'background-color: #fafafa; color: #000000; border: 1px solid #dee2e6',
        'Timing not right': 'background-color: #eeeeee; color: #000000; border: 1px solid #dee2e6',
        'Cold call done': 'background-color: #e0e0e0; color: #000000; border: 1px solid #dee2e6'
    }
    
    return stage_colors.get(value, 'background-color: #ffffff; color: #000000; border: 1px solid #dee2e6')

def main():
    """Main dashboard function"""
    
    # Logo and title
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image("https://via.placeholder.com/100x100/20B2AA/FFFFFF?text=M", width=80)
    with col2:
        st.title("🤖 Maxim AI Sales Pipeline Analysis")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🔄 Refresh Data", help="Pull fresh data from HubSpot API", type="primary"):
            refresh_data_from_hubspot()
    
    # Load data
    with st.spinner("Loading deal data..."):
        df = load_and_process_data()
    
    if df is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Analysis Configuration
    st.subheader("📅 Analysis Configuration")
    
    # Get date range from data
    data_min_date = df['created_at'].min().date() if not df.empty else datetime.now().date()
    data_max_date = df['created_at'].max().date() if not df.empty else datetime.now().date()
    
    # Initialize session state for quick options
    if 'frequency' not in st.session_state:
        st.session_state.frequency = 'Weekly'
    if 'analysis_start_date' not in st.session_state:
        st.session_state.analysis_start_date = data_min_date
    if 'analysis_end_date' not in st.session_state:
        st.session_state.analysis_end_date = min(data_max_date, datetime.now().date())
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("**Choose your analysis period:**")
        
        # Frequency selection
        frequency = st.selectbox(
            "Analysis frequency",
            options=['Daily', 'Weekly', 'Monthly'],
            index=['Daily', 'Weekly', 'Monthly'].index(st.session_state.frequency),
            help="How often to sample the data (daily, weekly, or monthly)",
            key="frequency_selectbox"
        )
        
        # Update session state when frequency changes
        st.session_state.frequency = frequency
        
        # Date range selection
        col_start, col_end = st.columns(2)
        
        with col_start:
            analysis_start_date = st.date_input(
                "Start date",
                value=st.session_state.analysis_start_date,
                min_value=data_min_date,
                max_value=data_max_date,
                help="Start date for the analysis period",
                key="start_date_input"
            )
        
        with col_end:
            analysis_end_date = st.date_input(
                "End date",
                value=st.session_state.analysis_end_date,
                min_value=data_min_date,
                max_value=data_max_date,
                help="End date for the analysis period",
                key="end_date_input"
            )
    
    with col2:
        st.markdown("**Quick Options:**")
        
        # Daily options
        if st.button("📅 Last 30 Days", help="Analyze the most recent 30 days (Daily frequency)"):
            st.session_state.frequency = 'Daily'
            st.session_state.analysis_end_date = datetime.now().date()
            st.session_state.analysis_start_date = st.session_state.analysis_end_date - timedelta(days=29)
            st.rerun()
        if st.button("📅 Last 60 Days", help="Analyze the most recent 60 days (Daily frequency)"):
            st.session_state.frequency = 'Daily'
            st.session_state.analysis_end_date = datetime.now().date()
            st.session_state.analysis_start_date = st.session_state.analysis_end_date - timedelta(days=59)
            st.rerun()
        
        # Weekly options
        if st.button("📊 Last 13 Weeks", help="Analyze the most recent 13 weeks (Weekly frequency)"):
            st.session_state.frequency = 'Weekly'
            st.session_state.analysis_end_date = datetime.now().date()
            st.session_state.analysis_start_date = st.session_state.analysis_end_date - timedelta(weeks=12)
            st.rerun()
        if st.button("📊 Last 54 Weeks", help="Analyze the most recent 54 weeks (Weekly frequency)"):
            st.session_state.frequency = 'Weekly'
            st.session_state.analysis_end_date = datetime.now().date()
            st.session_state.analysis_start_date = st.session_state.analysis_end_date - timedelta(weeks=53)
            st.rerun()
    
    with col3:
        st.markdown("**Monthly Options:**")
        
        # Monthly options
        if st.button("📆 Last 12 Months", help="Analyze the most recent 12 months (Monthly frequency)"):
            st.session_state.frequency = 'Monthly'
            st.session_state.analysis_end_date = datetime.now().date()
            end_year = st.session_state.analysis_end_date.year
            end_month = st.session_state.analysis_end_date.month
            if end_month == 1:
                start_year = end_year - 1
                start_month = 12
            else:
                start_year = end_year
                start_month = end_month - 1
            st.session_state.analysis_start_date = datetime(start_year, start_month, 1).date()
            st.rerun()
        if st.button("📆 Last 24 Months", help="Analyze the most recent 24 months (Monthly frequency)"):
            st.session_state.frequency = 'Monthly'
            st.session_state.analysis_end_date = datetime.now().date()
            end_year = st.session_state.analysis_end_date.year
            end_month = st.session_state.analysis_end_date.month
            if end_month <= 12:
                start_year = end_year - 2
                start_month = end_month
            else:
                start_year = end_year - 1
                start_month = end_month - 12
            st.session_state.analysis_start_date = datetime(start_year, start_month, 1).date()
            st.rerun()
        
    
    # Validate date range
    if analysis_start_date >= analysis_end_date:
        st.error("❌ Start date must be before end date")
        st.stop()
    
    # Calculate period count for display
    if frequency == 'Daily':
        period_count = (analysis_end_date - analysis_start_date).days + 1
        period_text = f"{period_count} days"
    elif frequency == 'Weekly':
        period_count = ((analysis_end_date - analysis_start_date).days // 7) + 1
        period_text = f"{period_count} weeks"
    elif frequency == 'Monthly':
        period_count = (analysis_end_date.year - analysis_start_date.year) * 12 + (analysis_end_date.month - analysis_start_date.month) + 1
        period_text = f"{period_count} months"
    
    # Display the analysis period
    st.info(f"🔍 **Analysis Period:** {analysis_start_date.strftime('%Y-%m-%d')} to {analysis_end_date.strftime('%Y-%m-%d')} ({period_text}, {frequency} frequency)")
    
    # Sidebar filters
    st.sidebar.header("🔍 Additional Filters")
    
    # Show all deals option
    show_all_deals = st.sidebar.checkbox(
        "Show All Deals",
        value=False,
        help="Bypass all filters to show all deals"
    )
    
    if show_all_deals:
        st.sidebar.warning("⚠️ All filters are bypassed - showing all deals")
    
    # Date range filter
    st.sidebar.subheader("Creation Date Range")
    min_date = df['created_at'].min().date() if not df.empty else datetime.now().date()
    max_date = df['created_at'].max().date() if not df.empty else datetime.now().date()
    
    if not show_all_deals:
        # Quick filter options for deal creation date
        st.sidebar.markdown("**Quick Options:**")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📅 Last 3 Months", help="Filter deals created in the last 3 months"):
                end_date = datetime.now().date()
                if end_date.month <= 3:
                    start_date = datetime(end_date.year - 1, end_date.month + 9, 1).date()
                else:
                    start_date = datetime(end_date.year, end_date.month - 3, 1).date()
                st.session_state.creation_date_range = (start_date, end_date)
                st.rerun()
            
            if st.button("📅 Last 6 Months", help="Filter deals created in the last 6 months"):
                end_date = datetime.now().date()
                if end_date.month <= 6:
                    start_date = datetime(end_date.year - 1, end_date.month + 6, 1).date()
                else:
                    start_date = datetime(end_date.year, end_date.month - 6, 1).date()
                st.session_state.creation_date_range = (start_date, end_date)
                st.rerun()
        
        with col2:
            if st.button("📅 All Time", help="Show all deals regardless of creation date"):
                st.session_state.creation_date_range = (min_date, max_date)
                st.rerun()
        
        # Initialize session state if not exists
        if 'creation_date_range' not in st.session_state:
            st.session_state.creation_date_range = (min_date, max_date)
        
        date_range = st.sidebar.date_input(
            "Select date range",
            value=st.session_state.creation_date_range,
            min_value=min_date,
            max_value=max_date
        )
        
        # Update session state when date range changes
        if len(date_range) == 2:
            st.session_state.creation_date_range = date_range
    else:
        date_range = (min_date, max_date)
    
    # Stage filter
    st.sidebar.subheader("Current Stage Filter")
    all_stages = ['Sign-up', 'Demo Booked', 'Demo Done', 'Customer Converted', 'Closed Won', 
                  'Junk', 'Not a good fit', 'Closed Lost', 'Churned', 'Relevant Reply',
                  'Outreach done', 'Post-demo follow-up', 'To reach out', 'Timing not right',
                  'Cold call done', 'No Show', 'Follow-up done', 'PoC not right but company relevant',
                  '$$$$ follow-ups', 'Active trial $$$$ #haisha']
    
    selected_stages = st.sidebar.multiselect(
        "Show only deals currently in these stages",
        options=all_stages,
        default=[]
    )
    
    # Deal name filter
    st.sidebar.subheader("Deal Name Filter")
    all_deals = sorted(df['dealname'].unique()) if not df.empty else []
    selected_deals = st.sidebar.multiselect(
        "Select specific deals (optional)",
        options=all_deals,
        default=[]
    )
    
    # Campaign filter
    st.sidebar.subheader("Lemlist Campaign Filter")
    if not df.empty and 'last_contact_lemlist_campaign' in df.columns:
        # Handle mixed data types (strings and NaN/float values)
        campaign_values = df['last_contact_lemlist_campaign'].dropna().astype(str).unique()
        all_campaigns = sorted([campaign for campaign in campaign_values if campaign and campaign.strip() and campaign != 'None' and campaign != 'nan'])
    else:
        all_campaigns = []
    
    selected_campaigns = st.sidebar.multiselect(
        "Select specific campaigns (optional)",
        options=all_campaigns,
        default=[],
        help="Filter deals by their associated contact's lemlist campaign"
    )
    
    # Stagnant deals filter
    st.sidebar.subheader("Stagnant Deals Filter")
    stagnant_threshold = st.sidebar.slider(
        "Show deals stagnant for more than N periods",
        min_value=1,
        max_value=20,
        value=3,
        help="Filter deals that haven't changed stage for more than N periods"
    )
    show_stagnant_only = st.sidebar.checkbox(
        "Show only stagnant deals",
        value=False,
        help="Show only deals that haven't changed stage for more than the threshold"
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if not show_all_deals:
        # Apply date range filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['created_at'].dt.date >= start_date) &
                (filtered_df['created_at'].dt.date <= end_date)
            ]
        
        # Apply deal selection filter
        if selected_deals:
            filtered_df = filtered_df[filtered_df['dealname'].isin(selected_deals)]
        
        # Apply campaign filter
        if selected_campaigns:
            # Handle mixed data types in campaign filtering
            filtered_df = filtered_df[filtered_df['last_contact_lemlist_campaign'].astype(str).isin(selected_campaigns)]
    
    st.info(f"📊 **Deals after filtering:** {len(filtered_df)}")
    
    # Create the period matrix
    with st.spinner(f"Creating {frequency.lower()} stage matrix..."):
        # Convert analysis dates to datetime objects
        analysis_start_datetime = datetime.combine(analysis_start_date, datetime.min.time())
        analysis_end_datetime = datetime.combine(analysis_end_date, datetime.min.time())
        
        matrix_df, period_dates = create_period_matrix(filtered_df, analysis_start_datetime, analysis_end_datetime, frequency)
    
    if matrix_df.empty:
        st.warning("No deals found for the selected filters.")
        return
    
    # Apply stage filter after creating matrix
    if selected_stages and not show_all_deals:
        # Get current stages (last non-empty column)
        period_columns = [col for col in matrix_df.columns if col not in ['Deal Name', 'Deal ID', 'Created', 'Lemlist Campaign']]
        before_stage_filter = len(matrix_df)
        matrix_df['Current Stage'] = matrix_df[period_columns].apply(
            lambda row: next((stage for stage in reversed(row) if stage), ''), axis=1
        )
        matrix_df = matrix_df[matrix_df['Current Stage'].isin(selected_stages)]
        matrix_df = matrix_df.drop('Current Stage', axis=1)
        after_stage_filter = len(matrix_df)
        st.sidebar.markdown(f"After stage filter: {after_stage_filter} (removed {before_stage_filter - after_stage_filter})")
    elif show_all_deals:
        st.sidebar.markdown("Stage filter bypassed")
    
    # Apply stagnant deals filter
    if show_stagnant_only:
        stagnant_df = calculate_stagnant_deals(matrix_df, period_dates, frequency)
        stagnant_deal_ids = stagnant_df[stagnant_df['stagnant_periods'] > stagnant_threshold]['deal_id'].tolist()
        before_stagnant_filter = len(matrix_df)
        matrix_df = matrix_df[matrix_df['Deal ID'].isin(stagnant_deal_ids)]
        after_stagnant_filter = len(matrix_df)
        st.sidebar.markdown(f"After stagnant filter: {after_stagnant_filter} (removed {before_stagnant_filter - after_stagnant_filter})")
        
        # Show stagnant deals summary
        if not stagnant_df.empty:
            st.sidebar.subheader("Stagnant Deals Summary")
            stagnant_summary = stagnant_df[stagnant_df['stagnant_periods'] > stagnant_threshold]
            if not stagnant_summary.empty:
                st.sidebar.dataframe(
                    stagnant_summary[['deal_name', 'current_stage', 'stagnant_periods']].rename(columns={
                        'deal_name': 'Deal',
                        'current_stage': 'Stage',
                        'stagnant_periods': 'Periods'
                    }),
                    height=200
                )
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Deals Shown", len(matrix_df))
    with col2:
        st.metric(f"{frequency} Periods Analyzed", len(period_dates))
    with col3:
        # Count deals with stage changes
        period_columns = [col for col in matrix_df.columns if col not in ['Deal Name', 'Deal ID', 'Created', 'Lemlist Campaign']]
        changes = 0
        for _, row in matrix_df.iterrows():
            stages = [stage for stage in row[period_columns] if stage]
            if len(set(stages)) > 1:  # More than one unique stage
                changes += 1
        st.metric("Deals with Stage Changes", changes)
    
    # Display the matrix
    st.subheader("📋 Deal Stage Matrix")
    st.markdown(f"**Showing {len(matrix_df)} deals across {len(period_dates)} {frequency.lower()} periods ({analysis_start_date.strftime('%Y-%m-%d')} to {analysis_end_date.strftime('%Y-%m-%d')})**")
    
    # Format the dataframe for better display
    display_df = matrix_df.copy()
    
    # Apply styling to period columns with better styling
    period_columns = [col for col in display_df.columns if col not in ['Deal Name', 'Deal ID', 'Created', 'Last Contact', 'Lemlist Campaign']]
    
    # Create styled dataframe with borders and better colors
    styled_df = display_df.style.map(style_cell, subset=period_columns)
    
    # Add header styling
    styled_df = styled_df.set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#343a40'),
            ('color', 'white'),
            ('border', '1px solid #dee2e6'),
            ('text-align', 'center'),
            ('font-weight', 'bold')
        ]},
        {'selector': 'td', 'props': [
            ('text-align', 'center'),
            ('font-size', '12px'),
            ('padding', '8px')
        ]},
        {'selector': 'tr:nth-child(even)', 'props': [
            ('background-color', '#f8f9fa')
        ]}
    ])
    
    # Display the table with proper frozen columns using CSS
    display_df_with_links = display_df.copy()
    
    # Get deal IDs and create HubSpot URLs
    deal_ids = display_df_with_links['Deal ID']
    portal_id = os.getenv('HUBSPOT_PORTAL_ID', 'your-portal-id')
    
    # Create clickable links for deal names
    deal_names = display_df_with_links['Deal Name']
    hubspot_urls = [f"https://app.hubspot.com/contacts/{portal_id}/deal/{deal_id}" for deal_id in deal_ids]
    
    # Create HTML links for deal names
    display_df_with_links['Deal Name'] = [f'<a href="{url}" target="_blank" style="color: #0066cc; text-decoration: none;">{name}</a>' for name, url in zip(deal_names, hubspot_urls)]
    
    # Create styled dataframe with HTML links
    styled_df_with_links = display_df_with_links.style.map(style_cell, subset=[col for col in display_df_with_links.columns if col not in ['Deal Name', 'Deal ID', 'Created', 'Lemlist Campaign']])
    
    # Add CSS for frozen columns - only freeze first 2 columns
    frozen_css = """
    <style>
    .dataframe {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        table-layout: fixed;
    }
    .dataframe th:first-child,
    .dataframe td:first-child {
        position: sticky !important;
        left: 0 !important;
        background-color: white !important;
        z-index: 10 !important;
        border-right: 2px solid #dee2e6 !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1) !important;
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
    }
    .dataframe th:nth-child(2),
    .dataframe td:nth-child(2) {
        position: sticky !important;
        left: 200px !important;
        background-color: white !important;
        z-index: 10 !important;
        border-right: 2px solid #dee2e6 !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1) !important;
        width: 100px !important;
        min-width: 100px !important;
        max-width: 100px !important;
    }
    .dataframe th:first-child {
        border-top-left-radius: 8px;
    }
    .dataframe td:first-child,
    .dataframe td:nth-child(2) {
        font-weight: 500;
        padding: 8px !important;
    }
    </style>
    """
    
    st.markdown(frozen_css, unsafe_allow_html=True)
    st.markdown(styled_df_with_links.to_html(escape=False), unsafe_allow_html=True)
    
    # Stage legend
    st.subheader("🎨 Stage Legend")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🟦 Positive Progression:**")
        st.markdown("🔵 Sign-up")
        st.markdown("🟡 Demo Booked") 
        st.markdown("🟣 Demo Done")
        st.markdown("🟢 Customer Converted")
        st.markdown("✅ Closed Won")
    
    with col2:
        st.markdown("**🔴 Negative Stages:**")
        st.markdown("🔴 Closed Lost")
        st.markdown("⚪ Junk")
        st.markdown("🔴 Not a good fit")
        st.markdown("🔴 Churned")
    
    with col3:
        st.markdown("**🟡 Other Stages:**")
        st.markdown("🔵 Relevant Reply")
        st.markdown("🟡 Outreach done")
        st.markdown("🟣 Post-demo follow-up")
        st.markdown("🟡 To reach out")
        st.markdown("🟡 Timing not right")
    
    # Export functionality
    st.subheader("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"deal_stage_matrix_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.info("💡 **Tip**: Use the filters in the sidebar to focus on specific deals or time periods")

if __name__ == "__main__":
    main()