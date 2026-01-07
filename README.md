# Open Hedge Fund 
An AI-powered hedge fund that uses multiple agents to make trading decisions, with Composio integration for multi-source financial data. This is an extension of[AI-Hedge-fund](https://github.com/virattt/ai-hedge-fund)


## Features

- 18+ AI analyst agents (Warren Buffett, Charlie Munger, etc.)
- Multi-source data via Composio (Finage, Alpha Vantage)
- Feature flag for easy data source switching
- Backtesting engine

## Quick Start

```bash
# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

## Data Sources

Toggle between data sources via `USE_COMPOSIO_DATA` environment variable:
- `true` - Use Composio (Finage/Alpha Vantage)
- `false` - Use Financial Datasets API
