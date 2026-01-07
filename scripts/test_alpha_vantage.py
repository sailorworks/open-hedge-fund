"""
Test script to verify Alpha Vantage connection via Composio.

This script:
1. Lists all connected accounts to find Alpha Vantage
2. Tests direct tool execution with Alpha Vantage
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
    print("=" * 60)
    print("Alpha Vantage Connection Test via Composio")
    print("=" * 60)
    
    if not COMPOSIO_API_KEY:
        print("ERROR: COMPOSIO_API_KEY not set in .env")
        return
    
    print(f"\n[CONFIG]")
    print(f"  COMPOSIO_API_KEY: {COMPOSIO_API_KEY[:20]}...")
    print(f"  AUTH_CONFIG_ID: {ALPHA_VANTAGE_AUTH_CONFIG_ID}")
    print(f"  USER_ID: {USER_ID}")
    
    # Initialize client with toolkit version
    client = Composio(
        api_key=COMPOSIO_API_KEY,
        toolkit_versions={"alpha_vantage": "20250101_00"}
    )
    
    # Step 1: List ALL connected accounts (not filtered by user)
    print(f"\n[STEP 1] Listing ALL connected accounts...")
    try:
        response = client.connected_accounts.list()
        # Handle ConnectedAccountListResponse - it may have .items or be iterable
        if hasattr(response, 'items'):
            all_accounts = response.items
        elif hasattr(response, '__iter__'):
            all_accounts = list(response)
        else:
            # Try to inspect the object
            print(f"  Response type: {type(response)}")
            print(f"  Response attrs: {dir(response)}")
            all_accounts = []
        
        print(f"  Found {len(all_accounts)} total connected accounts:")
        for acc in all_accounts:
            # Handle different response structures
            toolkit_name = getattr(acc, 'toolkit', None)
            if toolkit_name and hasattr(toolkit_name, 'slug'):
                toolkit_name = toolkit_name.slug
            elif hasattr(acc, 'toolkit_slug'):
                toolkit_name = acc.toolkit_slug
            else:
                toolkit_name = str(acc)
            
            status = getattr(acc, 'status', 'unknown')
            acc_id = getattr(acc, 'id', 'unknown')
            user = getattr(acc, 'user_id', 'unknown')
            print(f"    - {toolkit_name}: status={status}, id={acc_id}, user={user}")
    except Exception as e:
        print(f"  Error listing accounts: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 2: List connected accounts for our specific user
    print(f"\n[STEP 2] Listing connected accounts for user '{USER_ID}'...")
    try:
        response = client.connected_accounts.list(user_ids=[USER_ID])
        if hasattr(response, 'items'):
            user_accounts = response.items
        elif hasattr(response, '__iter__'):
            user_accounts = list(response)
        else:
            user_accounts = []
        
        print(f"  Found {len(user_accounts)} accounts for user '{USER_ID}':")
        for acc in user_accounts:
            toolkit_name = getattr(acc, 'toolkit', None)
            if toolkit_name and hasattr(toolkit_name, 'slug'):
                toolkit_name = toolkit_name.slug
            elif hasattr(acc, 'toolkit_slug'):
                toolkit_name = acc.toolkit_slug
            else:
                toolkit_name = str(acc)
            print(f"    - {toolkit_name}: {getattr(acc, 'status', 'unknown')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Step 3: Try to find Alpha Vantage account
    print(f"\n[STEP 3] Looking for Alpha Vantage connection...")
    alpha_vantage_account_id = None
    try:
        response = client.connected_accounts.list()
        if hasattr(response, 'items'):
            all_accounts = response.items
        elif hasattr(response, '__iter__'):
            all_accounts = list(response)
        else:
            all_accounts = []
        
        for acc in all_accounts:
            toolkit_name = getattr(acc, 'toolkit', None)
            if toolkit_name and hasattr(toolkit_name, 'slug'):
                toolkit_name = toolkit_name.slug.lower()
            elif hasattr(acc, 'toolkit_slug'):
                toolkit_name = acc.toolkit_slug.lower()
            else:
                continue
            
            if 'alpha' in toolkit_name or 'vantage' in toolkit_name:
                alpha_vantage_account_id = getattr(acc, 'id', None)
                print(f"  Found Alpha Vantage account: {alpha_vantage_account_id}")
                print(f"    Status: {getattr(acc, 'status', 'unknown')}")
                print(f"    User ID: {getattr(acc, 'user_id', 'unknown')}")
                break
        
        if not alpha_vantage_account_id:
            print("  No Alpha Vantage account found!")
            print("\n  You need to connect Alpha Vantage in Composio dashboard:")
            print("  1. Go to https://app.composio.dev")
            print("  2. Navigate to Connected Accounts")
            print("  3. Add Alpha Vantage with your API key")
            return
    except Exception as e:
        print(f"  Error: {e}")
        return
    
    # Step 4: Test direct tool execution
    print(f"\n[STEP 4] Testing ALPHA_VANTAGE_COMPANY_OVERVIEW for AAPL...")
    try:
        # Try with connected_account_id if we found one
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            connected_account_id=alpha_vantage_account_id,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS!")
        print(f"  Result type: {type(result)}")
        
        # Handle different response formats
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result.get('data', result)
        else:
            data = result
        
        if isinstance(data, dict):
            print(f"  Company: {data.get('Name', 'N/A')}")
            print(f"  Symbol: {data.get('Symbol', 'N/A')}")
            print(f"  Market Cap: {data.get('MarketCapitalization', 'N/A')}")
            print(f"  PE Ratio: {data.get('PERatio', 'N/A')}")
        else:
            print(f"  Raw result: {str(result)[:500]}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Test TIME_SERIES_DAILY
    print(f"\n[STEP 5] Testing ALPHA_VANTAGE_TIME_SERIES_DAILY for AAPL...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_TIME_SERIES_DAILY",
            connected_account_id=alpha_vantage_account_id,
            arguments={"symbol": "AAPL", "outputsize": "compact"}
        )
        print(f"  SUCCESS!")
        
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result.get('data', result)
        else:
            data = result
        
        if isinstance(data, dict):
            # Check for time series data
            time_series = data.get('Time Series (Daily)', {})
            if time_series:
                dates = list(time_series.keys())[:3]
                print(f"  Got {len(time_series)} days of data")
                print(f"  Latest dates: {dates}")
                if dates:
                    latest = time_series[dates[0]]
                    print(f"  Latest close: {latest.get('4. close', 'N/A')}")
            else:
                print(f"  Response keys: {list(data.keys())[:5]}")
        else:
            print(f"  Raw result: {str(result)[:500]}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
