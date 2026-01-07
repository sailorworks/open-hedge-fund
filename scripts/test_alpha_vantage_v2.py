"""
Test script v2 - Try different approaches to execute Alpha Vantage tools
"""
import os
from dotenv import load_dotenv
load_dotenv()

from composio import Composio

COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
ALPHA_VANTAGE_ACCOUNT_ID = "ca_xA-BLlkUOMsP"  # From previous test

def main():
    print("=" * 60)
    print("Alpha Vantage Tool Execution Test v2")
    print("=" * 60)
    
    # Test 1: Without toolkit_versions
    print("\n[TEST 1] Client WITHOUT toolkit_versions...")
    client1 = Composio(api_key=COMPOSIO_API_KEY)
    
    try:
        result = client1.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            connected_account_id=ALPHA_VANTAGE_ACCOUNT_ID,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS! Result: {str(result)[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 2: List available tools for alpha_vantage
    print("\n[TEST 2] Listing available Alpha Vantage tools...")
    try:
        # Try to get tools for the toolkit
        tools = client1.tools.get(
            connected_account_id=ALPHA_VANTAGE_ACCOUNT_ID,
            tools=["ALPHA_VANTAGE_COMPANY_OVERVIEW"]
        )
        print(f"  Tools response: {tools}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 3: Try with user_id from the connected account
    print("\n[TEST 3] Execute with user_id='soboardsvantage'...")
    try:
        result = client1.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            user_id="soboardsvantage",
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS! Result: {str(result)[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: Try listing all tools
    print("\n[TEST 4] Listing all available tools (first 20)...")
    try:
        # Check if there's a tools.list method
        if hasattr(client1.tools, 'list'):
            tools_list = client1.tools.list()
            if hasattr(tools_list, 'items'):
                tools_list = tools_list.items
            print(f"  Found tools: {len(tools_list) if hasattr(tools_list, '__len__') else 'unknown count'}")
            # Look for alpha vantage tools
            for tool in list(tools_list)[:50]:
                name = getattr(tool, 'name', getattr(tool, 'slug', str(tool)))
                if 'alpha' in str(name).lower() or 'vantage' in str(name).lower():
                    print(f"    - {name}")
        else:
            print("  No tools.list method available")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 5: Try the proxy execute approach
    print("\n[TEST 5] Try proxy execute to Alpha Vantage API directly...")
    try:
        # This uses Composio to inject auth and call the API directly
        result = client1.tools.proxy_execute(
            connected_account_id=ALPHA_VANTAGE_ACCOUNT_ID,
            endpoint="/query",
            method="GET",
            parameters={
                "function": "OVERVIEW",
                "symbol": "AAPL"
            }
        )
        print(f"  SUCCESS! Result: {str(result)[:300]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 6: Check the connected account details
    print("\n[TEST 6] Get connected account details...")
    try:
        account = client1.connected_accounts.get(ALPHA_VANTAGE_ACCOUNT_ID)
        print(f"  Account ID: {account.id}")
        print(f"  Status: {account.status}")
        print(f"  Toolkit: {account.toolkit}")
        if hasattr(account, 'toolkit') and hasattr(account.toolkit, 'slug'):
            print(f"  Toolkit slug: {account.toolkit.slug}")
        if hasattr(account, 'state'):
            print(f"  Auth scheme: {account.state.auth_scheme if account.state else 'N/A'}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
