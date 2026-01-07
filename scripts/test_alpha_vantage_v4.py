"""
Test script v4 - Search for Alpha Vantage toolkit and tools
"""
import os
from dotenv import load_dotenv
load_dotenv()

from composio import Composio

COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
USER_ID = "soboardsvantage"

def main():
    print("=" * 60)
    print("Alpha Vantage Toolkit Search v4")
    print("=" * 60)
    
    client = Composio(api_key=COMPOSIO_API_KEY)
    
    # Test 1: List all toolkits and find alpha_vantage
    print("\n[TEST 1] Searching for Alpha Vantage in available toolkits...")
    try:
        response = client.toolkits.list()
        if hasattr(response, 'items'):
            toolkits = response.items
        else:
            toolkits = list(response)
        
        alpha_vantage_found = False
        for tk in toolkits:
            slug = getattr(tk, 'slug', '')
            name = getattr(tk, 'name', '')
            if 'alpha' in slug.lower() or 'vantage' in slug.lower() or 'alpha' in name.lower():
                alpha_vantage_found = True
                print(f"  FOUND: {name} (slug: {slug})")
                meta = getattr(tk, 'meta', None)
                if meta:
                    print(f"    Description: {getattr(meta, 'description', 'N/A')[:100]}...")
                    print(f"    Tools count: {getattr(meta, 'tools_count', 'N/A')}")
                    print(f"    Version: {getattr(meta, 'version', 'N/A')}")
        
        if not alpha_vantage_found:
            print("  Alpha Vantage NOT found in available toolkits!")
            print("  Searching for financial toolkits...")
            for tk in toolkits:
                slug = getattr(tk, 'slug', '')
                name = getattr(tk, 'name', '')
                meta = getattr(tk, 'meta', None)
                categories = []
                if meta and hasattr(meta, 'categories'):
                    categories = [c.name for c in meta.categories if hasattr(c, 'name')]
                if 'financial' in str(categories).lower() or 'finance' in str(categories).lower():
                    print(f"    - {name} (slug: {slug})")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try to get tools directly
    print("\n[TEST 2] Getting tools for user with ALPHA_VANTAGE toolkit...")
    try:
        tools = client.tools.get(
            user_id=USER_ID,
            toolkits=["ALPHA_VANTAGE"]
        )
        print(f"  Response type: {type(tools)}")
        if isinstance(tools, list) and len(tools) > 0:
            print(f"  Got {len(tools)} tools!")
            for tool in tools[:5]:
                if isinstance(tool, dict):
                    func = tool.get('function', {})
                    print(f"    - {func.get('name', 'unknown')}")
                else:
                    print(f"    - {tool}")
        else:
            print(f"  Tools: {tools}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 3: Try with version
    print("\n[TEST 3] Execute with explicit version...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            user_id=USER_ID,
            version="20251208_00",  # Try the version from toolkit list
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS! Result: {str(result)[:300]}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: Try with connected_account_id and version
    print("\n[TEST 4] Execute with connected_account_id and version...")
    try:
        result = client.tools.execute(
            "ALPHA_VANTAGE_COMPANY_OVERVIEW",
            connected_account_id="ca_xA-BLlkUOMsP",
            version="20251208_00",
            arguments={"symbol": "AAPL"}
        )
        print(f"  SUCCESS! Result: {str(result)[:300]}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
