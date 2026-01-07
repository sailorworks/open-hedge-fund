"""
Composio Tool Execution Module for AI Hedge Fund

This module provides direct tool execution via Composio SDK.
Uses the simplified direct execution pattern (not Tool Router sessions)
since we know exactly which tools to call.

Based on Composio SDK documentation:
- composio.tools.execute(tool_name, user_id=..., arguments=...)
"""

import os
from typing import Any
from src.tools.composio_client import get_composio_client

# Default user ID for scoping connected accounts
# This must match the user_id used when connecting the account in Composio
_default_user_id = os.environ.get("COMPOSIO_USER_ID", "soboardsvantage")


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """
    Execute a Composio tool directly.
    
    This uses the direct execution pattern from Composio SDK:
    composio.tools.execute(tool_name, user_id=..., arguments=...)
    
    Args:
        tool_name: The name of the tool to execute 
                   (e.g., 'FINAGE_GET_STOCK_HISTORICAL_DATA')
        arguments: Dictionary of arguments for the tool
        
    Returns:
        dict: Result with 'successful' boolean and 'data' or 'error' key
    """
    print(f"[COMPOSIO] Executing tool: {tool_name}")
    print(f"[COMPOSIO] Arguments: {arguments}")
    
    client = get_composio_client()
    
    try:
        # Direct tool execution per Composio SDK docs
        # Tool name is first positional argument
        result = client.tools.execute(
            tool_name,
            user_id=_default_user_id,
            arguments=arguments
        )
        print(f"[COMPOSIO] Success: Got response from {tool_name}")
        return {"successful": True, "data": result}
    except Exception as e:
        print(f"[COMPOSIO] Error ({tool_name}): {e}")
        return {"successful": False, "error": str(e)}


def get_user_id() -> str:
    """Get the current user ID used for tool execution."""
    return _default_user_id
