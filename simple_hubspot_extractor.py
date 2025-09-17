#!/usr/bin/env python3
"""
Simple HubSpot Deal Stage Properties Extractor

This script extracts specific deal stage properties from HubSpot and saves them to a CSV file.
"""

import requests
import csv
import time
import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# CONFIGURATION - Set your HubSpot access token via environment variable
# =============================================================================
HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
if not HUBSPOT_ACCESS_TOKEN:
    raise ValueError("HUBSPOT_ACCESS_TOKEN environment variable is required. Please set it before running the script.")
# =============================================================================

class SimpleHubSpotExtractor:
    def __init__(self, access_token: str):
        """
        Initialize the HubSpot API client
        
        Args:
            access_token: HubSpot private app access token
        """
        self.access_token = access_token
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_properties_to_extract(self) -> List[str]:
        """
        Get the properties to extract
        
        Returns:
            List of property names
        """
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
    
    def get_all_deals(self, properties: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve all deals with specified properties
        
        Args:
            properties: List of property names to retrieve
            limit: Number of deals per request (max 100)
            
        Returns:
            List of deal records
        """
        all_deals = []
        after = None
        page = 1
        
        print(f"Extracting deals with {len(properties)} properties...")
        
        while True:
            try:
                url = f"{self.base_url}/crm/v3/objects/deals"
                params = {
                    "properties": ",".join(properties),
                    "limit": limit
                }
                
                if after:
                    params["after"] = after
                
                print(f"Fetching page {page}...")
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    deals = data.get("results", [])
                    all_deals.extend(deals)
                    
                    print(f"Retrieved {len(deals)} deals from page {page}")
                    
                    # Check if there are more pages
                    paging = data.get("paging", {})
                    after = paging.get("next", {}).get("after")
                    
                    if not after:
                        break
                    
                    page += 1
                    time.sleep(0.1)  # Rate limiting
                    
                else:
                    print(f"Error fetching deals: {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                break
        
        print(f"Total deals retrieved: {len(all_deals)}")
        return all_deals
    
    def export_to_csv(self, deals: List[Dict[str, Any]], output_file: str):
        """
        Export deals to CSV file
        
        Args:
            deals: List of deal records
            output_file: Output CSV file path
        """
        if not deals:
            print("No deals to export")
            return
        
        # Get the properties we're interested in
        target_properties = self.get_properties_to_extract()
        
        # Add standard fields
        fieldnames = ["deal_id", "created_at", "updated_at"] + target_properties
        
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
                    
                    # Add only the target properties
                    properties = deal.get("properties", {})
                    for prop in target_properties:
                        row[prop] = properties.get(prop, "")
                    
                    writer.writerow(row)
            
            print(f"Successfully exported {len(deals)} deals to {output_file}")
            
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
    
    def run_extraction(self, output_file: str = None):
        """
        Run the complete extraction process
        
        Args:
            output_file: Optional output CSV file path
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"hubspot_deals_{timestamp}.csv"
        
        # Get properties to extract
        properties = self.get_properties_to_extract()
        
        print(f"Extracting {len(properties)} properties:")
        for i, prop in enumerate(properties, 1):
            print(f"  {i:2d}. {prop}")
        
        # Retrieve all deals
        deals = self.get_all_deals(properties)
        
        if deals:
            # Export to CSV
            self.export_to_csv(deals, output_file)
        else:
            print("No deals found or error occurred during extraction")

def main():
    """
    Main function to run the extraction
    """
    # Initialize extractor
    extractor = SimpleHubSpotExtractor(HUBSPOT_ACCESS_TOKEN)
    
    # Run extraction
    extractor.run_extraction()

if __name__ == "__main__":
    main()
