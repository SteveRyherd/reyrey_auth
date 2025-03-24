# Reynolds & Reynolds CRM Authentication Module

A Python module for handling authentication with the Reynolds & Reynolds CRM system.

## Features

- Multiple token storage providers (environment variables, JSON files, database, API)
- Token validation functionality
- Automated Playwright-based authentication for obtaining new tokens
- Configurable token provider system

## Installation

### From Local Directory

```bash
# Clone the repository
git clone https://github.com/yourusername/reyrey_auth.git
cd reyrey_auth

# Install in development mode
pip install -e .

# Or install as a regular package
pip install .
```

### From Git Repository

```bash
pip install git+https://github.com/yourusername/reyrey_auth.git
```

## Configuration

Set up your credentials in a `.env` file:

```
REYREY_USERNAME=your_username
REYREY_PASSWORD=your_password
```

You can customize token storage locations:

```python
from reyrey_auth import configure

# Optional: Configure paths
configure(
    token_dir="/custom/path/to/tokens",
    db_path="/custom/path/to/database.db",
    json_path="/custom/path/to/token.json"
)
```

## Basic Usage

```python
from reyrey_auth import get_token, get_auth_headers

# Get a token (will use Playwright to get a new token if needed)
token = get_token(use_playwright_if_missing=True)

# Get headers for API requests
headers = get_auth_headers()

# Make authenticated requests
import requests
response = requests.get("https://focus.dealer.reyrey.net/api/endpoint", headers=headers)
```

## Advanced Usage

```python
import asyncio
from reyrey_auth import get_authenticated_session

async def example():
    # Get an authenticated browser session
    context, page, token = await get_authenticated_session()
    
    # Use the session for browser automation
    await page.goto("https://focus.dealer.reyrey.net/some/page")
    
    # Clean up when done
    await page.close()
    await context.close()

# Run the async function
asyncio.run(example())
```

## Token Providers

The module supports multiple token providers:

1. **Environment File Provider**: Stores tokens in a `.env` file
2. **JSON File Provider**: Stores tokens in a JSON file
3. **Database Provider**: Stores tokens in a SQLite database
4. **API Provider**: Retrieves tokens from an API server

You can configure which providers to use:

```python
from reyrey_auth import get_token

# Specify which providers to try, in order of preference
token = get_token(providers=["env_file", "json_file"])
```

## Custom Token Providers

You can create custom token providers:

```python
from reyrey_auth.providers.base import TokenProvider
from reyrey_auth import register_provider

class MyCustomProvider(TokenProvider):
    @property
    def name(self):
        return "custom"
    
    def get_token(self, token_name):
        # Your implementation here
        pass
    
    def save_token(self, token, token_name, domain):
        # Your implementation here
        pass

# Register your provider
register_provider(MyCustomProvider())
```
