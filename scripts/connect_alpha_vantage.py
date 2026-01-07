"""
Script to connect Alpha Vantage to your Composio account.

Prerequisites:
1. Get a free Alpha Vantage API key from: https://www.alphavantage.co/support/#api-key
2. Create an auth config in Composio dashboard for Alpha Vantage
3. Run this script with your auth config ID
"""
import os
from dotenv import load_dotenv
load_dotenv()

from composio import Composio

# Configuration
COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
ALPHA_VANTAGE_AUTH_CONFIG_ID = os.environ.get('ALPHA_VANTAGE_AUTH_CONFIG_ID', 'ac_YKcYX9fHgAGW')
USER_ID = "hedge-fund-agent"

def main():
    print("=== Alpha Vantage Connection Setup ===\n")
    
    if not COMPOSIO_API_KEY:
        print("ERROR: COMPOSIO_API_KEY not set in .env")
        return
    
    client = Composio(api_key=COMPOSIO_API_KEY)
    
    # Check if already connected
    print("Checking existing connections...")
    try:
        accounts = client.connected_accounts.list(user_ids=[USER_ID])
        for acc in accounts:
            print(f"  - {acc.toolkit.slug}: {acc.status}")
            if acc.toolkit.slug.lower() == 'alpha_vantage':
                print(f"\n✓ Alpha Vantage already connected! Account ID: {acc.id}")
                return
    except Exception as e:
        print(f"  Error listing accounts: {e}")
    
    # Connect Alpha Vantage
    print("\nAlpha Vantage not connected. Starting connection...")
    print(f"Using auth config: {ALPHA_VANTAGE_AUTH_CONFIG_ID}")
    
    # Get API key from user
    api_key = input("\nEnter your Alpha Vantage API key (get free key at https://www.alphavantage.co/support/#api-key): ").strip()
    
    if not api_key:
        print("ERROR: API key required")
        return
    
    try:
        connection_request = client.connected_accounts.initiate(
            user_id=USER_ID,
            auth_config_id=ALPHA_VANTAGE_AUTH_CONFIG_ID,
            config={
                "auth_scheme": "API_KEY",
                "val": {"generic_api_key": api_key}
            }
        )
        print(f"\n✓ Successfully connected Alpha Vantage!")
        print(f"  Connection ID: {connection_request.id}")
        print(f"  Status: {connection_request.status}")
    except Exception as e:
        print(f"\nERROR connecting: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you created an auth config for Alpha Vantage in Composio dashboard")
        print("2. Copy the auth config ID (starts with 'ac_') to your .env file")
        print("3. Get a free API key from https://www.alphavantage.co/support/#api-key")

if __name__ == "__main__":
    main()
