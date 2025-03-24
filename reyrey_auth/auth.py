"""
Authentication module for Reynolds & Reynolds CRM.
Provides token management and Playwright-based authentication.
"""

import os
import asyncio
import concurrent.futures
from datetime import datetime, timezone

from .utils.logger import logger
from .providers import get_provider, _default_provider_order
from .config import config

# ------------------------------------------------------
# Token Validation Functions
# ------------------------------------------------------

def check_token_validity(token, token_name='DRT'):
    """
    Check if a token is still valid via the API
    
    Args:
        token: Token value to check
        token_name: Name of the token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        import requests
        
        # Prepare request
        url = f"https://authservice.dealer.reyrey.net/api/Utils/CheckToken?Token={token}"
        
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': '*/*',
            'Origin': 'https://focus.dealer.reyrey.net',
            'Referer': 'https://focus.dealer.reyrey.net/',
            'Token': token
        }
        
        # Make the request
        response = requests.post(url, headers=headers, json={}, timeout=5)
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info(f"Token {token_name} is valid")
            
            # Check if the response includes a tokenexpiry header
            if 'tokenexpiry' in response.headers:
                expiry = response.headers.get('tokenexpiry')
                logger.info(f"Token expires at: {expiry}")
                
            return True
        else:
            logger.warning(f"Token {token_name} is invalid (status code: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking token validity: {str(e)}")
        # If we can't reach the server, we should assume the token might still be valid
        # to prevent unnecessary login attempts
        return True
    except Exception as e:
        logger.error(f"Unexpected error checking token validity: {str(e)}")
        return False

# ------------------------------------------------------
# Token Management Functions
# ------------------------------------------------------

def get_token(token_name='DRT', providers=None, use_playwright_if_missing=False, check_token=True):
    """
    Get an authentication token from the configured providers
    
    Args:
        token_name: Name of the token to retrieve
        providers: List of provider names to try (default: all registered providers)
        use_playwright_if_missing: Whether to use Playwright to get a token if none found
        check_token: Whether to verify token validity before returning
        
    Returns:
        str: Token value or None if not found or invalid
    """
    # Determine which providers to use
    if providers is None:
        providers = _default_provider_order
    
    # Try each provider
    for provider_name in providers:
        provider = get_provider(provider_name)
        if provider:
            token = provider.get_token(token_name)
            if token:
                # Verify token validity if requested
                if check_token and not check_token_validity(token, token_name):
                    logger.warning(f"Found token is invalid, will try other providers or get a new one")
                    continue
                
                return token
    
    # If no token found and Playwright fallback is enabled
    if use_playwright_if_missing:
        logger.info("No valid token found, attempting to get new token via Playwright")
        try:
            # Create a new event loop for this specific function
            # This addresses the issue when called from another async context
            token = None
            if asyncio.get_event_loop().is_running():
                # We're in an async context, create a new thread to run asyncio.run
                def run_async_get_token():
                    return asyncio.run(get_new_token(token_name))
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async_get_token)
                    try:
                        token = future.result(timeout=60)  # 60 second timeout
                    except concurrent.futures.TimeoutError:
                        logger.error("Timeout while getting new token")
            else:
                # We're in a sync context, can use asyncio.run directly
                token = asyncio.run(get_new_token(token_name))
                
            if token:
                logger.info("Successfully obtained new token via Playwright")
                return token
        except Exception as e:
            logger.error(f"Failed to get new token via Playwright: {str(e)}")
    
    logger.warning(f"Valid token {token_name} not found")
    return None

def save_token(token, token_name='DRT', domain='focus.dealer.reyrey.net', providers=None):
    """
    Save a token to all configured providers
    
    Args:
        token: Token value
        token_name: Name of the token
        domain: Domain the token is for
        providers: List of provider names to use (default: all registered providers)
        
    Returns:
        bool: True if saved to at least one provider
    """
    # Determine which providers to use
    if providers is None:
        providers = _default_provider_order
    
    success = False
    
    # Save to each provider
    for provider_name in providers:
        provider = get_provider(provider_name)
        if provider:
            if provider.save_token(token, token_name, domain):
                success = True
    
    return success

# ------------------------------------------------------
# Playwright Authentication Functions
# ------------------------------------------------------

async def login_to_crm():
    """
    Handle authentication to the Reynolds & Reynolds Focus CRM system
    
    Returns:
        tuple: (context, page) - Playwright browser context and page objects
    """
    logger.info("Initiating login to CRM")
    
    # Get credentials
    from dotenv import load_dotenv
    load_dotenv()
    username = os.getenv("REYREY_USERNAME")
    password = os.getenv("REYREY_PASSWORD")
    
    if not username or not password:
        raise ValueError("Missing credentials in environment variables REYREY_USERNAME and REYREY_PASSWORD")
    
    # Import here to avoid requiring playwright for basic token operations
    from playwright.async_api import async_playwright
    
    p = await async_playwright().start()
    # Launch browser (using chromium by default)
    browser = await p.chromium.launch(headless=config.headless)
    context = await browser.new_context()
    
    # Create a new page
    page = await context.new_page()
        
    try:
        # Navigate to the login page
        await page.goto("https://focus.dealer.reyrey.net/")
        logger.info("Navigated to login page")
        
        # Wait for the login form to be visible
        await page.wait_for_selector('input[name="UserName"]', timeout=10000)
        
        # Fill in username and password fields
        await page.fill('input[name="UserName"]', username)
        await page.fill('input[name="Password"]', password)
        
        # Try multiple selectors for the login button
        button_selectors = [
            'input[value="Sign On"]',
            'input[name="Sign On"]',
            'input[type="submit"]',
            'input.submitButton',
            'button[type="submit"]',
            'button:has-text("Sign On")'
        ]
        
        # Try each selector until one works
        for selector in button_selectors:
            if await page.query_selector(selector):
                logger.info(f"Found login button with selector: {selector}")
                await page.click(selector)
                break
        else:
            # If none of the selectors work, try JavaScript click
            logger.warning("No selectors matched, trying JavaScript click")
            await page.evaluate('''() => {
                const buttons = document.querySelectorAll('input[type="submit"], button[type="submit"]');
                if (buttons.length > 0) buttons[0].click();
            }''')
        
        # Wait for navigation to complete
        await page.wait_for_load_state("networkidle")
        
        # Verify successful login by checking for dashboard elements
        logger.info(f"Verifying login at URL: {page.url}")
        
        # Wait longer for page to fully load
        await page.wait_for_load_state("networkidle", timeout=15000)
        
        # Save screenshot for debugging
        screenshot_path = os.path.join(config.token_directory, "logs", "login_result.png")
        await page.screenshot(path=screenshot_path)
        logger.info(f"Saved screenshot to {screenshot_path}")
        
        # Check for various success indicators
        success_selectors = [
            'text="SALES GOALS"', 
            'text="ACTIVITY OVERVIEW"',
            'text="My Clients"',
            'a:has-text("Logout")',
            '.dashboard-container',
            '.user-menu'
        ]
        
        # Try each selector
        for selector in success_selectors:
            try:
                if await page.wait_for_selector(selector, timeout=1000, state="attached"):
                    logger.info(f"Login verified with selector: {selector}")
                    return context, page
            except Exception:
                continue
        
        # If we get here, no success selectors were found
        page_content = await page.content()
        logger.debug(f"Page content excerpt: {page_content[:500]}...")
        
        # Check for error messages
        error_message = await page.text_content('.error-message') if await page.query_selector('.error-message') else "Unknown error"
        logger.error(f"Login verification failed: {error_message}")
        raise Exception(f"Login verification failed: {error_message}")
        
    except Exception as e:
        logger.error(f"Login process failed: {str(e)}")
        await browser.close()
        raise

async def extract_token_from_page(page, token_name='DRT'):
    """
    Extract authentication token from the page
    
    Args:
        page: Playwright page object
        token_name: Name of the token/cookie to extract
        
    Returns:
        str: Token value
    """
    logger.info(f"Attempting to extract {token_name} token")
    
    try:
        # Try to find the specified token in cookies
        token = await page.evaluate(f'''() => {{
            return document.cookie.split('; ')
                .find(row => row.startsWith('{token_name}='))
                ?.split('=')[1];
        }}''')
        
        if token:
            logger.info(f"{token_name} token found: {token[:10]}...")
            return token
            
        # If specified token not found, try FOCUSINUSE as fallback
        if token_name != 'FOCUSINUSE':
            token = await page.evaluate('''() => {
                return document.cookie.split('; ')
                    .find(row => row.startsWith('FOCUSINUSE='))
                    ?.split('=')[1];
            }''')
            
            if token:
                logger.info(f"FOCUSINUSE token found: {token[:10]}...")
                return token
                
        # Log all cookies for debugging
        cookies = await page.context.cookies()
        cookie_names = [cookie['name'] for cookie in cookies]
        logger.debug(f"Available cookies: {cookie_names}")
        
        raise ValueError(f"Could not extract {token_name} token")
        
    except Exception as e:
        logger.error(f"Token extraction failed: {str(e)}")
        raise

async def get_new_token(token_name='DRT'):
    """
    Log in to CRM and get a new authentication token
    
    Args:
        token_name: Name of the token/cookie to extract
        
    Returns:
        str: Token value
    """
    context = None
    page = None
    
    try:
        context, page = await login_to_crm()
        token = await extract_token_from_page(page, token_name)
        
        # Save the token to all providers
        save_token(token, token_name, domain='focus.dealer.reyrey.net')
        
        return token
    finally:
        # Clean up resources
        if page:
            try:
                await page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {str(e)}")
                
        if context:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {str(e)}")

async def get_authenticated_session(token=None, token_name='DRT', check_token=True):
    """
    Get an authenticated Playwright session, either by logging in or using an existing token
    
    Args:
        token: Optional existing token to use for authentication
        token_name: Name of the token/cookie to use
        check_token: Whether to verify token validity before using
        
    Returns:
        tuple: (context, page, token) - Playwright browser context, page and the authentication token
    """
    # If no token is provided, try to get one from providers
    if token is None:
        token = get_token(token_name=token_name, check_token=check_token)
    
    # If we have a token and should check it, verify it's valid
    if token and check_token:
        is_valid = check_token_validity(token, token_name)
        if not is_valid:
            logger.warning(f"Provided token is invalid, will attempt login instead")
            token = None
    
    # Import here to avoid requiring playwright for basic token operations
    from playwright.async_api import async_playwright
    
    # If we have a valid token, try to create a session with it
    if token:
        try:
            logger.info("Creating browser session with existing token")
            
            p = await async_playwright().start()
            browser = await p.chromium.launch(headless=config.headless)
            context = await browser.new_context()
            
            # Set the authentication cookie
            await context.add_cookies([{
                'name': token_name,
                'value': token,
                'domain': 'focus.dealer.reyrey.net',
                'path': '/',
            }])
            
            # Create a new page
            page = await context.new_page()
            
            # Navigate directly to the landing page
            await page.goto("https://focus.dealer.reyrey.net/?bg=100037")
            logger.info("Navigated to landing page with existing token")
            
            # Verify we're actually logged in by checking for dashboard elements
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            # Check for various success indicators
            success_selectors = [
                'text="SALES GOALS"', 
                'text="ACTIVITY OVERVIEW"',
                'text="My Clients"',
                'a:has-text("Logout")',
                '.dashboard-container',
                '.user-menu'
            ]
            
            # Try each selector
            for selector in success_selectors:
                try:
                    if await page.wait_for_selector(selector, timeout=1000, state="attached"):
                        logger.info(f"Token authentication verified with selector: {selector}")
                        logger.info("Successfully created authenticated session using existing token")
                        return context, page, token
                except Exception:
                    continue
                    
            # If we reach here, token authentication failed
            logger.warning("Token authentication failed, falling back to login")
            await page.close()
            await context.close()
            # Fall through to login process
        except Exception as e:
            logger.error(f"Error creating session with token: {str(e)}")
            # Fall through to login process
    
    # If we reach here, either we had no token or token authentication failed
    try:
        context, page = await login_to_crm()
        token = await extract_token_from_page(page, token_name)
        
        # Save the token but keep the session open
        save_token(token, token_name)
        
        logger.info("Successfully created authenticated session via login")
        return context, page, token
    except Exception as e:
        logger.error(f"Failed to create authenticated session: {str(e)}")
        raise

# ------------------------------------------------------
# Helper Functions
# ------------------------------------------------------

def get_auth_headers(token_name='DRT', check_token=True):
    """
    Get authentication headers for API requests
    
    Args:
        token_name: Name of the token to use
        check_token: Whether to verify token validity before returning
        
    Returns:
        dict: Headers with authentication token
    """
    token = get_token(token_name=token_name, use_playwright_if_missing=True, check_token=check_token)
    
    if not token:
        logger.error("Failed to get authentication token")
        return None
    
    return {
        'Content-Type': 'application/json;charset=utf-8',
        'Accept': '*/*',
        'Origin': 'https://focus.dealer.reyrey.net',
        'Referer': 'https://focus.dealer.reyrey.net/',
        'Token': token
    }
