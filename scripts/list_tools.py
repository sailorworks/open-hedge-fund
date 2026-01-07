"""Script to list available Composio tools."""
from composio import Composio
import os
from dotenv import load_dotenv
load_dotenv()

client = Composio(api_key=os.environ.get('COMPOSIO_API_KEY'))

# List available toolkits
print('=== Available Toolkits ===')
try:
    toolkits = client.toolkits.get()
    for tk in toolkits[:30]:
        print(f'  - {tk.slug}')
except Exception as e:
    print(f'Error listing toolkits: {e}')

# Try to find financial tools
print()
print('=== Searching for financial toolkits ===')
for name in ['finage', 'alpha_vantage', 'alphavantage', 'FINAGE', 'ALPHA_VANTAGE']:
    try:
        tools = client.tools.get_raw_composio_tools(toolkits=[name], limit=10)
        print(f'{name}: Found {len(tools)} tools')
        for t in tools[:10]:
            print(f'  - {t.name}')
    except Exception as e:
        print(f'{name}: Error - {str(e)[:100]}')
