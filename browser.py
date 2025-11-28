"""
Browser Automation Module using Playwright
Handles JavaScript-rendered pages and content extraction
"""

from playwright.async_api import async_playwright
import logging
import base64

logger = logging.getLogger(__name__)


async def get_page_content(url: str, timeout: int = 30000) -> str:
    """
    Fetch and render page content using headless browser

    Args:
        url: The URL to visit
        timeout: Timeout in milliseconds (default 30s)

    Returns:
        Rendered HTML content as string
    """
    logger.info(f"Fetching page content from: {url}")

    async with async_playwright() as p:
        try:
            # Launch headless browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                # Set user agent to avoid bot detection
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            # Navigate to URL
            await page.goto(url, timeout=timeout, wait_until="networkidle")

            # Wait a bit for any dynamic content to load
            await page.wait_for_timeout(2000)

            # Get the rendered HTML
            content = await page.content()

            # Also get the text content of the body for easier parsing
            text_content = await page.evaluate("() => document.body.innerText")

            await browser.close()

            logger.info(f"Successfully fetched {len(content)} bytes from {url}")

            return content

        except Exception as e:
            logger.error(f"Error fetching page content: {e}")
            raise


async def extract_quiz_details(html_content: str) -> dict:
    """
    Extract quiz question and details from HTML content

    Args:
        html_content: Raw HTML from the quiz page

    Returns:
        Dictionary with question, submit_url, and raw_html
    """
    from bs4 import BeautifulSoup

    logger.info("Parsing quiz page HTML")

    soup = BeautifulSoup(html_content, 'html.parser')

    # The quiz content is often base64 encoded in a script tag
    # Example: document.querySelector("#result").innerHTML = atob(`...`);

    # Try to find base64-encoded content
    scripts = soup.find_all('script')
    decoded_content = None

    for script in scripts:
        if script.string and 'atob' in script.string:
            # Extract the base64 string
            try:
                # Find content between backticks after atob(
                script_text = script.string
                start = script_text.find('atob(`') + 6
                end = script_text.find('`)', start)
                b64_string = script_text[start:end].strip()

                # Decode base64
                decoded_bytes = base64.b64decode(b64_string)
                decoded_content = decoded_bytes.decode('utf-8')
                logger.info("Successfully decoded base64 quiz content")
                break
            except Exception as e:
                logger.warning(f"Failed to decode base64: {e}")

    # If we found decoded content, parse it
    if decoded_content:
        # Parse the decoded HTML
        quiz_soup = BeautifulSoup(decoded_content, 'html.parser')

        # Extract the question (usually the main text content)
        question = quiz_soup.get_text(strip=True)

        # Extract submit URL (look for it in links or pre/code tags)
        submit_url = None
        for link in quiz_soup.find_all('a'):
            href = link.get('href', '')
            if 'submit' in href:
                submit_url = href
                break

        # Also check in pre or code blocks for the submit URL
        if not submit_url:
            for pre in quiz_soup.find_all(['pre', 'code']):
                text = pre.get_text()
                if 'submit' in text.lower():
                    # Try to extract URL from JSON-like text
                    import re
                    urls = re.findall(r'https?://[^\s"\']+', text)
                    for url in urls:
                        if 'submit' in url:
                            submit_url = url
                            break

        return {
            "question": question,
            "submit_url": submit_url,
            "decoded_html": decoded_content,
            "raw_html": html_content
        }
    else:
        # No base64 encoding, use the HTML as-is
        question = soup.get_text(strip=True)

        # Look for submit URL
        submit_url = None
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'submit' in href:
                submit_url = href
                break

        return {
            "question": question,
            "submit_url": submit_url,
            "decoded_html": html_content,
            "raw_html": html_content
        }
