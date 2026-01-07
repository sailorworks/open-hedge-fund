import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

def test_routing():
    print("--- Testing Feature Flag Routing ---")
    
    # Test 1: Default (should be original API)
    os.environ["USE_COMPOSIO_DATA"] = "false"
    import importlib
    from src.tools import api
    importlib.reload(api)
    
    print(f"USE_COMPOSIO_DATA=false: get_prices is from {api.get_prices.__module__}")
    
    # Test 2: Composio enabled
    os.environ["USE_COMPOSIO_DATA"] = "true"
    os.environ["COMPOSIO_API_KEY"] = "mock_key" # Just for import test
    importlib.reload(api)
    
    print(f"USE_COMPOSIO_DATA=true: get_prices is from {api.get_prices.__module__}")
    
    if "composio_data" in api.get_prices.__module__:
        print("✅ SUCCESS: Routing works correctly!")
    else:
        print("❌ FAILURE: Routing failed!")

def test_composio_logic():
    print("\n--- Testing Composio Logic (Mocked) ---")
    # We can't easily run real Composio calls without a real key, 
    # but we can check if the file compiles and functions are available.
    try:
        from src.tools import composio_data
        print("✅ SUCCESS: composio_data.py is valid and imports correctly.")
        
        required_funcs = [
            'get_prices', 'get_financial_metrics', 'search_line_items',
            'get_company_news', 'get_market_cap', 'get_insider_trades'
        ]
        
        for func in required_funcs:
            if hasattr(composio_data, func):
                print(f"✅ Found function: {func}")
            else:
                print(f"❌ Missing function: {func}")
                
    except Exception as e:
        print(f"❌ FAILURE: Error importing composio_data: {e}")

if __name__ == "__main__":
    test_routing()
    test_composio_logic()
