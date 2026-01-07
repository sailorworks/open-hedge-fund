import os
from composio import Composio

# Singleton client instance
_client = None

# Toolkit versions for Finage and Alpha Vantage
# Format: YYYYMMDD_NN (use recent stable versions)
TOOLKIT_VERSIONS = {
    "finage": "20250101_00",
    "alpha_vantage": "20250101_00",
}

def get_composio_client() -> Composio:
    """
    Get or create the Composio client singleton with toolkit versions configured.
    
    Returns:
        Composio: Authenticated client instance with versioning
        
    Raises:
        ValueError: If COMPOSIO_API_KEY environment variable is not set
    """
    global _client
    if _client is None:
        api_key = os.environ.get("COMPOSIO_API_KEY")
        if not api_key:
            raise ValueError("COMPOSIO_API_KEY environment variable is required")
        
        # Initialize with toolkit versions per Composio SDK docs
        _client = Composio(
            api_key=api_key,
            toolkit_versions=TOOLKIT_VERSIONS
        )
        print(f"[COMPOSIO_CLIENT] Initialized with versions: {TOOLKIT_VERSIONS}")
    return _client
