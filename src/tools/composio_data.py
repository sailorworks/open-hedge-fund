"""
Composio Data Layer for AI Hedge Fund

This module provides financial data through Composio's direct tool execution,
using Finage and Alpha Vantage toolkits with automatic fallback.

Based on Composio SDK documentation:
- Direct tool execution via composio.tools.execute()
- No Tool Router sessions needed for programmatic data fetching

Usage:
    Set USE_COMPOSIO_DATA=true and COMPOSIO_API_KEY in environment.
    Function signatures match api.py exactly for drop-in replacement.
"""

from typing import Optional
from src.data.cache import get_cache
from src.tools.composio_session import execute_tool as _execute_tool
from src.data.models import (
    CompanyNews,
    FinancialMetrics,
    Price,
    LineItem,
    InsiderTrade,
)

# Global cache instance (reuse existing infrastructure)
_cache = get_cache()


# ============================================================================
# PRICE DATA
# ============================================================================

def get_prices(ticker: str, start_date: str, end_date: str, api_key: str = None) -> list[Price]:
    """
    Fetch price data using Composio (Finage primary, Alpha Vantage fallback).
    
    Args:
        ticker: Stock symbol (e.g., "AAPL")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_key: Unused, kept for backward compatibility
    
    Returns:
        List of Price objects with OHLCV data
    """
    print(f"[COMPOSIO_DATA] get_prices called for {ticker} ({start_date} to {end_date})")
    
    # Check cache first
    cache_key = f"composio_{ticker}_{start_date}_{end_date}"
    if cached_data := _cache.get_prices(cache_key):
        print(f"[COMPOSIO_DATA] Cache HIT for prices {ticker}")
        return [Price(**price) for price in cached_data]

    print(f"[COMPOSIO_DATA] Cache MISS - fetching from Composio...")
    prices = []
    
    # Try Finage first (better historical data)
    print(f"[COMPOSIO_DATA] Trying FINAGE_GET_STOCK_HISTORICAL_DATA...")
    result = _execute_tool(
        "FINAGE_GET_STOCK_HISTORICAL_DATA",
        {
            "symbol": ticker,
            "from_date": start_date,
            "to_date": end_date,
            "time_unit": "day",
            "multiplier": 1
        }
    )
    
    if result.get("successful") and result.get("data"):
        print(f"[COMPOSIO_DATA] Finage returned data, transforming...")
        prices = _transform_finage_prices(result["data"])
    
    # Fallback to Alpha Vantage if Finage fails
    if not prices:
        print(f"[COMPOSIO_DATA] Finage failed, trying ALPHA_VANTAGE_TIME_SERIES_DAILY...")
        result = _execute_tool(
            "ALPHA_VANTAGE_TIME_SERIES_DAILY",
            {
                "symbol": ticker,
                "outputsize": "compact"  # Free tier: last 100 data points
            }
        )
        if result.get("successful") and result.get("data"):
            print(f"[COMPOSIO_DATA] Alpha Vantage returned data, transforming...")
            prices = _transform_alpha_vantage_prices(result["data"], start_date, end_date)
    
    if prices:
        print(f"[COMPOSIO_DATA] Got {len(prices)} prices, caching...")
        _cache.set_prices(cache_key, [p.model_dump() for p in prices])
    else:
        print(f"[COMPOSIO_DATA] No prices returned from any source!")
    
    return prices


def _transform_finage_prices(data: dict) -> list[Price]:
    """Transform Finage response to Price objects."""
    prices = []
    # Finage returns results in data.results array
    results = data.get("results", [])
    for item in results:
        try:
            prices.append(Price(
                open=float(item.get("o", 0)),
                high=float(item.get("h", 0)),
                low=float(item.get("l", 0)),
                close=float(item.get("c", 0)),
                volume=int(item.get("v", 0)),
                time=item.get("t", "")  # Timestamp
            ))
        except (ValueError, TypeError) as e:
            print(f"Error transforming Finage price data: {e}")
            continue
    return prices


def _transform_alpha_vantage_prices(data: dict, start_date: str, end_date: str) -> list[Price]:
    """Transform Alpha Vantage response to Price objects."""
    prices = []
    
    # Handle nested response structure from Composio
    # execute_tool returns: {"successful": True, "data": <composio_response>}
    # composio_response is: {"data": {"Time Series (Daily)": {...}}, "successful": true}
    # So 'data' here is the composio_response
    
    inner_data = data
    if "data" in data and isinstance(data["data"], dict):
        inner_data = data["data"]
    
    # Alpha Vantage returns time series in "Time Series (Daily)" key
    time_series = inner_data.get("Time Series (Daily)", {})
    
    print(f"[COMPOSIO_DATA] Found {len(time_series)} time series entries")
    
    for date_str, values in time_series.items():
        # Filter by date range
        if start_date <= date_str <= end_date:
            try:
                prices.append(Price(
                    open=float(values.get("1. open", 0)),
                    high=float(values.get("2. high", 0)),
                    low=float(values.get("3. low", 0)),
                    close=float(values.get("4. close", 0)),
                    volume=int(float(values.get("5. volume", 0))),
                    time=date_str
                ))
            except (ValueError, TypeError) as e:
                print(f"Error transforming Alpha Vantage price data: {e}")
                continue
    
    # Sort by date
    prices.sort(key=lambda p: p.time)
    print(f"[COMPOSIO_DATA] Filtered to {len(prices)} prices in date range")
    return prices


# ============================================================================
# FINANCIAL METRICS
# ============================================================================

def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
    api_key: str = None,
) -> list[FinancialMetrics]:
    """
    Fetch financial metrics using Alpha Vantage Company Overview.
    
    Args:
        ticker: Stock symbol
        end_date: End date for metrics
        period: Period type (ttm, annual, quarterly)
        limit: Number of records to return
        api_key: Unused, kept for backward compatibility
    
    Returns:
        List of FinancialMetrics objects
    """
    print(f"[COMPOSIO_DATA] get_financial_metrics called for {ticker}")
    
    cache_key = f"composio_metrics_{ticker}_{period}_{end_date}_{limit}"
    if cached_data := _cache.get_financial_metrics(cache_key):
        print(f"[COMPOSIO_DATA] Cache HIT for metrics {ticker}")
        return [FinancialMetrics(**metric) for metric in cached_data]

    print(f"[COMPOSIO_DATA] Cache MISS - fetching from Composio...")
    print(f"[COMPOSIO_DATA] Trying ALPHA_VANTAGE_COMPANY_OVERVIEW...")
    result = _execute_tool(
        "ALPHA_VANTAGE_COMPANY_OVERVIEW",
        {"symbol": ticker}
    )
    
    if not result.get("successful") or not result.get("data"):
        print(f"[COMPOSIO_DATA] Alpha Vantage Company Overview failed!")
        return []
    
    print(f"[COMPOSIO_DATA] Got company overview, transforming...")
    metrics = _transform_company_overview(result["data"], ticker, end_date, period)
    
    if metrics:
        print(f"[COMPOSIO_DATA] Got {len(metrics)} metrics, caching...")
        _cache.set_financial_metrics(cache_key, [m.model_dump() for m in metrics])
    
    return metrics[:limit]


def _transform_company_overview(data: dict, ticker: str, end_date: str, period: str) -> list[FinancialMetrics]:
    """Transform Alpha Vantage Company Overview to FinancialMetrics."""
    try:
        # Handle nested response structure from Composio
        # Response is: {"data": {...company data...}, "successful": true}
        if "data" in data and isinstance(data["data"], dict) and "Symbol" in data["data"]:
            inner_data = data["data"]
        else:
            inner_data = data
        
        print(f"[COMPOSIO_DATA] Company overview keys: {list(inner_data.keys())[:10]}...")
        
        metrics = FinancialMetrics(
            ticker=ticker,
            report_period=end_date,
            period=period,
            currency=inner_data.get("Currency", "USD"),
            market_cap=_safe_float(inner_data.get("MarketCapitalization")),
            enterprise_value=_safe_float(inner_data.get("EnterpriseValue")),
            price_to_earnings_ratio=_safe_float(inner_data.get("PERatio")),
            price_to_book_ratio=_safe_float(inner_data.get("PriceToBookRatio")),
            price_to_sales_ratio=_safe_float(inner_data.get("PriceToSalesRatioTTM")),
            enterprise_value_to_ebitda_ratio=_safe_float(inner_data.get("EVToEBITDA")),
            enterprise_value_to_revenue_ratio=_safe_float(inner_data.get("EVToRevenue")),
            free_cash_flow_yield=None,  # Not directly available
            peg_ratio=_safe_float(inner_data.get("PEGRatio")),
            gross_margin=_safe_float(inner_data.get("GrossProfitTTM")),  # Note: This is absolute, not margin
            operating_margin=_safe_float(inner_data.get("OperatingMarginTTM")),
            net_margin=_safe_float(inner_data.get("ProfitMargin")),
            return_on_equity=_safe_float(inner_data.get("ReturnOnEquityTTM")),
            return_on_assets=_safe_float(inner_data.get("ReturnOnAssetsTTM")),
            return_on_invested_capital=None,  # Not directly available
            asset_turnover=None,
            inventory_turnover=None,
            receivables_turnover=None,
            days_sales_outstanding=None,
            operating_cycle=None,
            working_capital_turnover=None,
            current_ratio=None,
            quick_ratio=None,
            cash_ratio=None,
            operating_cash_flow_ratio=None,
            debt_to_equity=None,
            debt_to_assets=None,
            interest_coverage=None,
            revenue_growth=_safe_float(inner_data.get("QuarterlyRevenueGrowthYOY")),
            earnings_growth=_safe_float(inner_data.get("QuarterlyEarningsGrowthYOY")),
            book_value_growth=None,
            earnings_per_share_growth=None,
            free_cash_flow_growth=None,
            operating_income_growth=None,
            ebitda_growth=None,
            payout_ratio=_safe_float(inner_data.get("PayoutRatio")),
            earnings_per_share=_safe_float(inner_data.get("EPS")),
            book_value_per_share=_safe_float(inner_data.get("BookValue")),
            free_cash_flow_per_share=None,
        )
        return [metrics]
    except Exception as e:
        print(f"Error transforming company overview: {e}")
        return []


def _safe_float(value) -> Optional[float]:
    """Safely convert a value to float, returning None on failure."""
    if value is None or value == "None" or value == "-":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# ============================================================================
# LINE ITEMS (Financial Statements)
# ============================================================================

def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
    api_key: str = None,
) -> list[LineItem]:
    """
    Fetch financial statement line items using Alpha Vantage.
    
    Combines Balance Sheet, Income Statement, and Cash Flow data.
    """
    all_items = []
    
    # Fetch all three financial statements
    statements = [
        ("ALPHA_VANTAGE_BALANCE_SHEET", "annualReports", "quarterlyReports"),
        ("ALPHA_VANTAGE_INCOME_STATEMENT", "annualReports", "quarterlyReports"),
        ("ALPHA_VANTAGE_CASH_FLOW", "annualReports", "quarterlyReports"),
    ]
    
    for tool_name, annual_key, quarterly_key in statements:
        result = _execute_tool(tool_name, {"symbol": ticker})
        
        if result.get("successful") and result.get("data"):
            data = result["data"]
            # Use quarterly or annual based on period
            reports_key = quarterly_key if period in ["quarterly", "ttm"] else annual_key
            reports = data.get("data", {}).get(reports_key, [])
            
            for report in reports[:limit]:
                fiscal_date = report.get("fiscalDateEnding", "")
                if fiscal_date and fiscal_date <= end_date:
                    # Extract requested line items
                    item_data = {
                        "ticker": ticker,
                        "report_period": fiscal_date,
                        "period": period,
                        "currency": report.get("reportedCurrency", "USD"),
                    }
                    # Add requested line items
                    for li in line_items:
                        if li in report:
                            item_data[li] = _safe_float(report[li])
                    
                    all_items.append(LineItem(**item_data))
    
    return all_items[:limit]


# ============================================================================
# COMPANY NEWS
# ============================================================================

def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
    api_key: str = None,
) -> list[CompanyNews]:
    """
    Fetch company news using Composio (Finage primary, Alpha Vantage fallback).
    """
    cache_key = f"composio_news_{ticker}_{start_date or 'none'}_{end_date}_{limit}"
    if cached_data := _cache.get_company_news(cache_key):
        return [CompanyNews(**news) for news in cached_data]

    news_items = []
    
    # Try Finage first
    result = _execute_tool(
        "FINAGE_GET_STOCK_MARKET_NEWS",
        {"symbol": ticker, "limit": min(limit, 50)}  # Finage limit
    )
    
    if result.get("successful") and result.get("data"):
        news_items = _transform_finage_news(result["data"], ticker)
    
    # Fallback to Alpha Vantage
    if not news_items:
        result = _execute_tool(
            "ALPHA_VANTAGE_NEWS_SENTIMENT",
            {
                "tickers": ticker,
                "limit": min(limit, 50),
                "time_from": start_date.replace("-", "") + "T0000" if start_date else None,
                "time_to": end_date.replace("-", "") + "T2359" if end_date else None,
            }
        )
        if result.get("successful") and result.get("data"):
            news_items = _transform_alpha_vantage_news(result["data"], ticker)
    
    if news_items:
        _cache.set_company_news(cache_key, [n.model_dump() for n in news_items])
    
    return news_items[:limit]


def _transform_finage_news(data: dict, ticker: str) -> list[CompanyNews]:
    """Transform Finage news response to CompanyNews objects."""
    news_items = []
    articles = data.get("articles", data.get("news", []))
    
    for article in articles:
        try:
            news_items.append(CompanyNews(
                ticker=ticker,
                title=article.get("title", ""),
                author=article.get("author", "Unknown"),
                source=article.get("source", "Finage"),
                date=article.get("publishedAt", article.get("date", "")),
                url=article.get("url", ""),
                sentiment=None
            ))
        except Exception as e:
            print(f"Error transforming Finage news: {e}")
            continue
    
    return news_items


def _transform_alpha_vantage_news(data: dict, ticker: str) -> list[CompanyNews]:
    """Transform Alpha Vantage news response to CompanyNews objects."""
    news_items = []
    feed = data.get("data", {}).get("feed", [])
    
    for article in feed:
        try:
            # Extract sentiment for the specific ticker
            ticker_sentiments = article.get("ticker_sentiment", [])
            sentiment = None
            for ts in ticker_sentiments:
                if ts.get("ticker") == ticker:
                    sentiment = ts.get("ticker_sentiment_label")
                    break
            
            news_items.append(CompanyNews(
                ticker=ticker,
                title=article.get("title", ""),
                author=article.get("author", "Unknown"),
                source=article.get("source", "Alpha Vantage"),
                date=article.get("time_published", ""),
                url=article.get("url", ""),
                sentiment=sentiment
            ))
        except Exception as e:
            print(f"Error transforming Alpha Vantage news: {e}")
            continue
    
    return news_items


# ============================================================================
# MARKET CAP
# ============================================================================

def get_market_cap(
    ticker: str,
    end_date: str,
    api_key: str = None,
) -> float | None:
    """
    Fetch market cap using Alpha Vantage Company Overview.
    """
    result = _execute_tool(
        "ALPHA_VANTAGE_COMPANY_OVERVIEW",
        {"symbol": ticker}
    )
    
    if result.get("successful") and result.get("data"):
        return _safe_float(result["data"].get("MarketCapitalization"))
    
    # Fallback: try to get from financial metrics
    metrics = get_financial_metrics(ticker, end_date)
    if metrics:
        return metrics[0].market_cap
    
    return None


# ============================================================================
# INSIDER TRADES (Fallback to original API - not available in Composio)
# ============================================================================

def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
    api_key: str = None,
) -> list[InsiderTrade]:
    """
    Fetch insider trades - falls back to Financial Datasets API.
    
    Note: Neither Finage nor Alpha Vantage provide insider trading data.
    This function imports from the original api.py for this specific data.
    """
    try:
        # Import the original function for insider trades
        from src.tools import api as original_api
        return original_api.get_insider_trades(ticker, end_date, start_date, limit, api_key)
    except ImportError:
        print("Warning: Original API not available for insider trades")
        return []


# ============================================================================
# UTILITY FUNCTIONS (Compatibility with api.py)
# ============================================================================

import pandas as pd

def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df


def get_price_data(ticker: str, start_date: str, end_date: str, api_key: str = None) -> pd.DataFrame:
    """Get price data as DataFrame."""
    prices = get_prices(ticker, start_date, end_date, api_key=api_key)
    return prices_to_df(prices)
