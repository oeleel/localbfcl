import os
import random
import re
import time
from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

ERROR_TEMPLATES = [
    "503 Server Error: Service Unavailable for url: {url}",
    "429 Client Error: Too Many Requests for url: {url}",
    "403 Client Error: Forbidden for url: {url}",
    (
        "HTTPSConnectionPool(host='{host}', port=443): Max retries exceeded with url: {path} "
        "(Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x{id1:x}>, "
        "'Connection to {host} timed out. (connect timeout=5)'))"
    ),
    "HTTPSConnectionPool(host='{host}', port=443): Read timed out. (read timeout=5)",
    (
        "Max retries exceeded with url: {path} "
        "(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x{id2:x}>: "
        "Failed to establish a new connection: [Errno -2] Name or service not known'))"
    ),
]


class WebSearchAPI:
    def __init__(self):
        self._api_description = "This tool belongs to the Web Search API category. It provides functions to search the web and browse search results."
        self.show_snippet = True
        # Note: The following two random generators are used to simulate random errors, but that feature is not currently used
        # This one used to determine if we should simulate a random error
        # Outcome (True means simulate error): [True, False, True, True, False, True, True, True, False, False, True, True, False, True, False, False, False, False, False, True]
        self._random = random.Random(337)
        # This one is used to determine the content of the error message
        self._rng = random.Random(1053)
        
        # Random insertion perturbation configuration
        self._enable_random_insertion = os.getenv("BFCL_ENABLE_RANDOM_INSERTION", "false").lower() == "true"
        self._random_insertion_rate = float(os.getenv("BFCL_RANDOM_INSERTION_RATE", "0.05"))
        self._random_insertion_text_pool = os.getenv(
            "BFCL_RANDOM_INSERTION_TEXT_POOL",
            "ADVERTISEMENT,[Sponsored],[Promoted],[Click here],[Learn more],...,***"
        ).split(",")
        # Use a separate random generator for perturbations to keep it reproducible if needed
        self._perturb_rng = random.Random(42)

    def _apply_random_insertion(self, text: str) -> str:
        """
        Apply random text insertion perturbation to the given text.
        
        Args:
            text: The text to perturb
            
        Returns:
            The text with random insertions applied
        """
        if not self._enable_random_insertion or not text:
            return text
        
        # Split text into words (preserving whitespace)
        # Use regex to split on whitespace while keeping the separators
        parts = re.split(r'(\s+)', text)
        
        # Apply random insertion
        perturbed_parts = []
        for part in parts:
            perturbed_parts.append(part)
            # Only insert after non-whitespace parts
            if part and not part.isspace():
                # Randomly decide to insert
                if self._perturb_rng.random() < self._random_insertion_rate:
                    insertion_text = self._perturb_rng.choice(self._random_insertion_text_pool)
                    # Insert with a space before and after
                    perturbed_parts.append(" " + insertion_text + " ")
        
        return "".join(perturbed_parts)
    
    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        # We don't care about the long_context parameter here
        # It's there to match the signature of functions in the multi-turn evaluation code
        self.show_snippet = initial_config["show_snippet"]

    def search_engine_query(
        self,
        keywords: str,
        max_results: Optional[int] = 10,
        region: Optional[str] = "wt-wt",
    ) -> list:
        """
        This function queries the search engine for the provided keywords and region.

        Args:
            keywords (str): The keywords to search for.
            max_results (int, optional): The maximum number of search results to return. Defaults to 10.
            region (str, optional): The region to search in. Defaults to "wt-wt". Possible values include:
                - xa-ar for Arabia
                - xa-en for Arabia (en)
                - ar-es for Argentina
                - au-en for Australia
                - at-de for Austria
                - be-fr for Belgium (fr)
                - be-nl for Belgium (nl)
                - br-pt for Brazil
                - bg-bg for Bulgaria
                - ca-en for Canada
                - ca-fr for Canada (fr)
                - ct-ca for Catalan
                - cl-es for Chile
                - cn-zh for China
                - co-es for Colombia
                - hr-hr for Croatia
                - cz-cs for Czech Republic
                - dk-da for Denmark
                - ee-et for Estonia
                - fi-fi for Finland
                - fr-fr for France
                - de-de for Germany
                - gr-el for Greece
                - hk-tzh for Hong Kong
                - hu-hu for Hungary
                - in-en for India
                - id-id for Indonesia
                - id-en for Indonesia (en)
                - ie-en for Ireland
                - il-he for Israel
                - it-it for Italy
                - jp-jp for Japan
                - kr-kr for Korea
                - lv-lv for Latvia
                - lt-lt for Lithuania
                - xl-es for Latin America
                - my-ms for Malaysia
                - my-en for Malaysia (en)
                - mx-es for Mexico
                - nl-nl for Netherlands
                - nz-en for New Zealand
                - no-no for Norway
                - pe-es for Peru
                - ph-en for Philippines
                - ph-tl for Philippines (tl)
                - pl-pl for Poland
                - pt-pt for Portugal
                - ro-ro for Romania
                - ru-ru for Russia
                - sg-en for Singapore
                - sk-sk for Slovak Republic
                - sl-sl for Slovenia
                - za-en for South Africa
                - es-es for Spain
                - se-sv for Sweden
                - ch-de for Switzerland (de)
                - ch-fr for Switzerland (fr)
                - ch-it for Switzerland (it)
                - tw-tzh for Taiwan
                - th-th for Thailand
                - tr-tr for Turkey
                - ua-uk for Ukraine
                - uk-en for United Kingdom
                - us-en for United States
                - ue-es for United States (es)
                - ve-es for Venezuela
                - vn-vi for Vietnam
                - wt-wt for No region

        Returns:
            list: A list of search result dictionaries, each containing information such as:
            - 'title' (str): The title of the search result.
            - 'href' (str): The URL of the search result.
            - 'body' (str): A brief description or snippet from the search result.
        """
        # Check which API to use (prefer Serper.dev if available)
        serper_api_key = os.getenv("SERPER_API_KEY")
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        use_serper = serper_api_key is not None
        
        if use_serper:
            # Serper.dev implementation
            return self._search_with_serper(keywords, max_results, region)
        elif serpapi_key:
            # SerpAPI implementation (fallback)
            return self._search_with_serpapi(keywords, max_results, region)
        else:
            # No API key configured
            error_msg = "No search API key configured. Please set either SERPER_API_KEY or SERPAPI_API_KEY in your .env file."
            print(f"❗️❗️ [WebSearchAPI] {error_msg}")
            # Return empty list instead of error dict to avoid empty response errors
            return []

    def _search_with_serper(
        self,
        keywords: str,
        max_results: Optional[int] = 10,
        region: Optional[str] = "wt-wt",
    ) -> list:
        """Search using Serper.dev API."""
        backoff = 2  # initial back-off in seconds
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        # Serper.dev uses country codes, but we'll pass gl (country) and hl (language) if needed
        # For now, we'll use the query as-is since region mapping is complex
        payload = {
            "q": keywords,
            "num": min(max_results, 10),  # Serper.dev supports up to 10 results per request
        }
        
        # Infinite retry loop with exponential backoff
        while True:
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                search_results = response.json()
                
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait_time = backoff + random.uniform(0, backoff)
                    error_block = (
                        "*" * 100
                        + f"\n❗️❗️ [WebSearchAPI] Received 429 from Serper.dev. Rate limit exceeded. Retrying in {wait_time:.1f} seconds…"
                        + "*" * 100
                    )
                    print(error_block)
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, 120)
                    continue
                else:
                    error_block = (
                        "*" * 100
                        + f"\n❗️❗️ [WebSearchAPI] Error from Serper.dev (HTTP {response.status_code}): {str(e)}. This is not a rate-limit error, so it will not be retried."
                        + "*" * 100
                    )
                    print(error_block)
                    # Return empty list instead of error dict to avoid empty response errors
                    return []
            except Exception as e:
                error_block = (
                    "*" * 100
                    + f"\n❗️❗️ [WebSearchAPI] Error from Serper.dev: {str(e)}. This is not a rate-limit error, so it will not be retried."
                    + "*" * 100
                )
                print(error_block)
                # Return empty list instead of error dict to avoid empty response errors
                return []
            
            break  # Success
        
        # Parse Serper.dev response format
        # Serper.dev returns results in "organic" key
        if "organic" not in search_results or not search_results["organic"]:
            # Return empty list instead of error dict to avoid empty response errors
            return []
        
        organic_results = search_results["organic"]
        
        # Convert to the desired format matching BFCL expectations
        results = []
        for result in organic_results[:max_results]:
            # Ensure all required fields exist with defaults to avoid KeyError
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            # Ensure title and link are not empty (required fields)
            if not title or not link:
                continue  # Skip invalid results
            
            if self.show_snippet:
                # Apply random insertion perturbation to the body/snippet
                body = self._apply_random_insertion(snippet) if snippet else ""
                results.append(
                    {
                        "title": title,
                        "href": link,
                        "body": body,
                    }
                )
            else:
                results.append(
                    {
                        "title": title,
                        "href": link,
                    }
                )
        
        # Always return a list, even if empty, to avoid empty response errors
        return results

    def _search_with_serpapi(
        self,
        keywords: str,
        max_results: Optional[int] = 10,
        region: Optional[str] = "wt-wt",
    ) -> list:
        """Search using SerpAPI (original implementation)."""
        backoff = 2  # initial back-off in seconds
        params = {
            "engine": "duckduckgo",
            "q": keywords,
            "kl": region,
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        # Infinite retry loop with exponential backoff
        while True:
            try:
                search = GoogleSearch(params)
                search_results = search.get_dict()
            except Exception as e:
                # If the underlying HTTP call raised a 429 we retry, otherwise propagate
                if "429" in str(e):
                    wait_time = backoff + random.uniform(0, backoff)
                    error_block = (
                        "*" * 100
                        + f"\n❗️❗️ [WebSearchAPI] Received 429 from SerpAPI. The number of requests sent using this API key exceeds the hourly throughput limit OR your account has run out of searches. Retrying in {wait_time:.1f} seconds…"
                        + "*" * 100
                    )
                    print(error_block)
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, 120)  # cap the back-off
                    continue
                else:
                    error_block = (
                        "*" * 100
                        + f"\n❗️❗️ [WebSearchAPI] Error from SerpAPI: {str(e)}. This is not a rate-limit error, so it will not be retried."
                        + "*" * 100
                    )
                    print(error_block)
                    # Return empty list instead of error dict to avoid empty response errors
                    return []

            # SerpAPI sometimes returns the error in the payload instead of raising
            if "error" in search_results and "429" in str(search_results["error"]):
                wait_time = backoff + random.uniform(0, backoff)
                error_block = (
                    "*" * 100
                    + f"\n❗️❗️ [WebSearchAPI] Received 429 from SerpAPI. The number of requests sent using this API key exceeds the hourly throughput limit OR your account has run out of searches. Retrying in {wait_time:.1f} seconds…"
                    + "*" * 100
                )
                print(error_block)
                time.sleep(wait_time)
                backoff = min(backoff * 2, 120)
                continue

            break  # Success – no rate-limit error detected

        if "organic_results" not in search_results or not search_results["organic_results"]:
            # Return empty list instead of error dict to avoid empty response errors
            return []

        search_results = search_results["organic_results"]

        # Convert the search results to the desired format
        results = []
        for result in search_results[:max_results]:
            # Ensure all required fields exist with defaults to avoid KeyError
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            # Ensure title and link are not empty (required fields)
            if not title or not link:
                continue  # Skip invalid results
            
            if self.show_snippet:
                # Apply random insertion perturbation to the body/snippet
                body = self._apply_random_insertion(snippet) if snippet else ""
                results.append(
                    {
                        "title": title,
                        "href": link,
                        "body": body,
                    }
                )
            else:
                results.append(
                    {
                        "title": title,
                        "href": link,
                    }
                )

        # Always return a list, even if empty, to avoid empty response errors
        return results

    def fetch_url_content(self, url: str, mode: str = "raw") -> str:
        """
        This function retrieves content from the provided URL and processes it based on the selected mode.

        Args:
            url (str): The URL to fetch content from. Must start with 'http://' or 'https://'.
            mode (str, optional): The mode to process the fetched content. Defaults to "raw".
                Supported modes are:
                    - "raw": Returns the raw HTML content.
                    - "markdown": Converts raw HTML content to Markdown format for better readability, using html2text.
                    - "truncate": Extracts and cleans text by removing scripts, styles, and extraneous whitespace.
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

        try:
            # A header that mimics a browser request. This helps avoid 403 Forbidden errors.
            # TODO: Is this the best way to do this?
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/112.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
            }
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            response.raise_for_status()

            # Note: Un-comment this when we want to simulate a random error
            # Flip a coin to simulate a random error
            # if self._random.random() < 0.95:
            #     return {"error": self._fake_requests_get_error_msg(url)}

            # Process the response based on the mode
            if mode == "raw":
                content = self._apply_random_insertion(response.text)
                return {"content": content}

            elif mode == "markdown":
                converter = html2text.HTML2Text()
                markdown = converter.handle(response.text)
                content = self._apply_random_insertion(markdown)
                return {"content": content}

            elif mode == "truncate":
                soup = BeautifulSoup(response.text, "html.parser")

                # Remove scripts and styles
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()

                # Extract and clean text
                text = soup.get_text(separator="\n", strip=True)
                content = self._apply_random_insertion(text)
                return {"content": content}
            else:
                raise ValueError(f"Unsupported mode: {mode}")

        except Exception as e:
            return {"error": f"An error occurred while fetching {url}: {str(e)}"}

    def _fake_requests_get_error_msg(self, url: str) -> str:
        """
        Return a realistic‑looking requests/urllib3 error message.
        """
        parsed = urlparse(url)

        context = {
            "url": url,
            "host": parsed.hostname or "unknown",
            "path": parsed.path or "/",
            "id1": self._rng.randrange(0x10000000, 0xFFFFFFFF),
            "id2": self._rng.randrange(0x10000000, 0xFFFFFFFF),
        }

        template = self._rng.choice(ERROR_TEMPLATES)

        return template.format(**context)
