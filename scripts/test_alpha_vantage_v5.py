"""
Test script v5 - Use correct toolkit version and check tool access
"""
import os
from dotenv import load_dotenv
load_dotenv()

from composio import Composio

COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
USER_ID = "soboardsvantage"
CONNECTED_ACCOUNT_ID = "ca_xA-BLlkUOMsP"
TOOLKIT_VERSION = "20260105_00"  # From toolkit list

def main():
    print("=" * 60)
    print("Alpha Vantage Test v5 - Correct Version")
    print("=" * 60)
    
    # Initialize with correct toolkit version
    client = Composio(
        api_key=COMPOSIO_API_KEY,
        toolkit_versions={"alpha_vantage": TOOLKIT_VERSION}
    )
    
    # Test 1: Get tools with correct version
    print("\n[TEST 1] Get tools with toolkit_versions configured...")
    try:
        tools = client.tools.get(
            user_id=USER_ID,
            toolkits=["alpha_vantage"]
        )
        print(f"  Response type: {type(tools)}")
        print(f"  Tools count: {len(tools) if isinstance(tools, list) else 'N/A'}")
        if isinstance(tools, list) and len(tools) > 0:
            for tool in tools[:5]:
                if isinstance(tool, dict):
                    func = tool.get('function', {})
                    print(f"    - {func.get('name', 'unknown')}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 2: Execute with version in toolkit_versions
    print("\n[TEST 2] Execute ALPHA_VANTAGE_COMPANY_OVERVIEW...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            user_id=USER_ID,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS!")
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result.get('data', result)
        else:
            data = result
        
        if isinstance(data, dict):
            print(f"  Company: {data.get('Name', data.get('name', 'N/A'))}")
            print(f"  Symbol: {data.get('Symbol', data.get('symbol', 'N/A'))}")
        else:
            print(f"  Result: {str(data)[:300]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 3: Execute with connected_account_id
    print("\n[TEST 3] Execute with connected_account_id...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            connected_account_id=CONNECTED_ACCOUNT_ID,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS!")
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result.get('data', result)
        else:
            data = result
        print(f"  Result: {str(data)[:300]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: Try lowercase tool name
    print("\n[TEST 4] Try lowercase tool name...")
    try:
        result = client.tools.execute(
            "alpha_vantage_company_overview",
            user_id=USER_ID,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS! Result: {str(result)[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 5: List tools from the toolkit directly
    print("\n[TEST 5] Get toolkit tools list...")
    try:
        # Try to get toolkit info
        if hasattr(client, 'toolkits') and hasattr(client.toolkits, 'get'):
            toolkit = client.toolkits.get("alpha_vantage")
            print(f"  Toolkit: {toolkit}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 6: Check if we need to use a different API
    print("\n[TEST 6] Try using tools.list with toolkit filter...")
    try:
        if hasattr(client.tools, 'list'):
            tools_response = client.tools.list(toolkit_slugs=["alpha_vantage"])
            if hasattr(tools_response, 'items'):
                tools = tools_response.items
            else:
                tools = list(tools_response) if hasattr(tools_response, '__iter__') else []
            print(f"  Found {len(tools)} tools")
            for tool in tools[:10]:
                slug = getattr(tool, 'slug', getattr(tool, 'name', str(tool)))
                print(f"    - {slug}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
