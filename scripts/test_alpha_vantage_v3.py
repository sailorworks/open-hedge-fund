"""
Test script v3 - Get tools using toolkits parameter
"""
import os
import json
from dotenv import load_dotenv
load_dotenv()

from composio import Composio

COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
USER_ID = "soboardsvantage"  # The user ID from the connected account

def main():
    print("=" * 60)
    print("Alpha Vantage Tool Discovery Test v3")
    print("=" * 60)
    
    client = Composio(api_key=COMPOSIO_API_KEY)
    
    # Test 1: Get tools for ALPHA_VANTAGE toolkit
    print("\n[TEST 1] Get tools for ALPHA_VANTAGE toolkit...")
    try:
        tools = client.tools.get(
            user_id=USER_ID,
            toolkits=["ALPHA_VANTAGE"]
        )
        print(f"  Got tools response type: {type(tools)}")
        if isinstance(tools, list):
            print(f"  Number of tools: {len(tools)}")
            for tool in tools[:10]:
                if isinstance(tool, dict):
                    print(f"    - {tool.get('name', tool.get('function', {}).get('name', 'unknown'))}")
                else:
                    print(f"    - {tool}")
        else:
            print(f"  Tools: {str(tools)[:500]}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try lowercase toolkit name
    print("\n[TEST 2] Get tools for 'alpha_vantage' toolkit (lowercase)...")
    try:
        tools = client.tools.get(
            user_id=USER_ID,
            toolkits=["alpha_vantage"]
        )
        print(f"  Got tools response type: {type(tools)}")
        if isinstance(tools, list):
            print(f"  Number of tools: {len(tools)}")
            for tool in tools[:5]:
                if isinstance(tool, dict):
                    name = tool.get('name', tool.get('function', {}).get('name', 'unknown'))
                    print(f"    - {name}")
                else:
                    print(f"    - {getattr(tool, 'name', str(tool)[:50])}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 3: Get specific tool
    print("\n[TEST 3] Get specific tool ALPHA_VANTAGE_COMPANY_OVERVIEW...")
    try:
        tools = client.tools.get(
            user_id=USER_ID,
            tools=["ALPHA_VANTAGE_COMPANY_OVERVIEW"]
        )
        print(f"  Got tools: {tools}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: Execute with the correct user_id
    print("\n[TEST 4] Execute ALPHA_VANTAGE_COMPANY_OVERVIEW...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            user_id=USER_ID,
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS!")
        print(f"  Result type: {type(result)}")
        if hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result.get('data', result)
        else:
            data = result
        print(f"  Data: {str(data)[:500]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 5: Check what toolkits are available
    print("\n[TEST 5] Check available toolkits...")
    try:
        # Try to list toolkits
        if hasattr(client, 'toolkits'):
            toolkits = client.toolkits.list() if hasattr(client.toolkits, 'list') else None
            print(f"  Toolkits: {toolkits}")
        else:
            print("  No toolkits attribute on client")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
