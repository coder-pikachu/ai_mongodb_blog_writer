from langchain.tools import Tool
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, List
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config.logging_config import setup_logging

load_dotenv()
logger = setup_logging(__name__)

class WebSearchTools:
    # Priority MongoDB news and documentation sources
    PRIORITY_SOURCES = [
        'mongodb.com/blog',
        'www.mongodb.com/docs',
        'www.mongodb.com/developer',
        'www.mongodb.com/community',
        'github.com/mongodb',
        'www.mongodb.com/changelog',
        'engineering.mongodb.com'
    ]

    # Technical blogs and trusted sources
    TECH_SOURCES = [
        'medium.com/tag/mongodb',
        'dev.to/t/mongodb',
        'dzone.com/mongodb',
        'infoq.com/mongodb',
        'stackoverflow.blog'
    ]

    @staticmethod
    def search_web() -> Tool:
        logger.info("Initializing web search tool")
        try:
            def serper_search(query: str) -> dict:
                """Perform a search using Serper.dev API"""
                url = "https://google.serper.dev/search"
                payload = json.dumps({"q": query})
                headers = {
                    'X-API-KEY': os.getenv('SERPER_API_KEY'),
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=payload)
                return response.json()

            def enhanced_search(query: str) -> str:
                """Enhanced search with source prioritization"""
                logger.info("Performing enhanced search for query: %s", query)
                try:
                    # Perform the search
                    search_results = serper_search(query)
                    
                    if not search_results or 'organic' not in search_results:
                        logger.warning("No results found for query: %s", query)
                        return "No relevant results found."

                    # Process and prioritize results
                    prioritized_results = []
                    other_results = []

                    for result in search_results.get('organic', []):
                        result_data = {
                            'title': result.get('title', ''),
                            'link': result.get('link', ''),
                            'snippet': result.get('snippet', ''),
                            'date': result.get('date', '')
                        }

                        # Check if result is from priority sources
                        is_priority = any(source in result.get('link', '').lower() 
                                        for source in WebSearchTools.PRIORITY_SOURCES)
                        
                        if is_priority:
                            prioritized_results.append(result_data)
                        else:
                            other_results.append(result_data)

                    # Combine results with priority ones first
                    all_results = prioritized_results + other_results
                    
                    # Format results as a string
                    formatted_results = []
                    for idx, result in enumerate(all_results[:5], 1):
                        formatted_result = (
                            f"{idx}. {result['title']}\n"
                            f"   URL: {result['link']}\n"
                            f"   Summary: {result['snippet']}\n"
                        )
                        if result.get('date'):
                            formatted_result += f"   Date: {result['date']}\n"
                        formatted_results.append(formatted_result)

                    return "\n".join(formatted_results) if formatted_results else "No relevant results found."

                except Exception as e:
                    logger.error("Error in enhanced search: %s", str(e))
                    return f"Error performing search: {str(e)}"

            return Tool(
                name="Web Search",
                func=enhanced_search,
                description="Search the web for MongoDB related information and news"
            )

        except Exception as e:
            logger.error("Failed to initialize web search tool: %s", str(e))
            raise

    @staticmethod
    def scrape_web() -> Tool:
        def scrape_site(url: str) -> Optional[str]:
            """Scrape text content from a webpage with enhanced cleaning"""
            logger.info("Scraping content from URL: %s", url)

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                logger.debug("Making HTTP request")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                logger.debug("Parsing HTML content")
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove unwanted elements
                logger.debug("Removing unwanted elements")
                for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    element.decompose()

                # Focus on main content areas
                logger.debug("Identifying main content area")
                main_content = None
                content_priorities = [
                    soup.find('article'),
                    soup.find('main'),
                    soup.find(class_='post-content'),
                    soup.find(class_='article-content'),
                    soup.find(id='content'),
                    soup.find(class_='content')
                ]

                for content in content_priorities:
                    if content:
                        main_content = content
                        logger.debug("Found main content using selector: %s", content.name)
                        break

                if not main_content:
                    logger.debug("No specific content area found, using entire body")
                    main_content = soup

                # Extract text with better formatting
                logger.debug("Extracting and formatting text content")
                text_parts = []
                for element in main_content.stripped_strings:
                    text = element.strip()
                    if text and len(text) > 20:  # Skip very short fragments
                        text_parts.append(text)

                # Join with proper spacing
                text = '\n\n'.join(text_parts)

                # Clean up extra whitespace
                text = '\n'.join(line for line in text.splitlines() if line.strip())

                # Add source attribution
                text = f"Source: {url}\n\n{text}"

                logger.info("Successfully scraped and processed content")
                return text[:8000]  # Return first 8000 characters

            except Exception as e:
                logger.error("Error scraping %s: %s", url, str(e))
                return f"Error scraping {url}: {str(e)}"

        return Tool(
            name="ScrapeWeb",
            func=scrape_site,
            description="""
            Enhanced web scraping tool optimized for MongoDB documentation and technical articles.
            Input should be a valid URL. Returns cleaned and formatted content with source attribution.
            """
        )

    @staticmethod
    def get_latest_mongodb_news() -> List[str]:
        """Gather latest MongoDB news from priority sources"""
        logger.info("Gathering latest MongoDB news")

        try:
            search = SerpAPIWrapper(

            )
            logger.debug("Serper API initialized for news gathering")

            # Calculate date for recent content
            one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            logger.debug("Searching for content after: %s", one_month_ago)

            news_items = []

            # Search each priority source for recent content
            for source in WebSearchTools.PRIORITY_SOURCES:
                try:
                    query = f"after:{one_month_ago} site:{source}"
                    logger.debug("Searching news from source: %s", source)
                    results = search.run(query)
                    if isinstance(results, dict) and 'organic' in results:
                        organic_results = results['organic']
                        formatted_results = "\n".join([
                            f"Title: {result.get('title', '')}\n"
                            f"Link: {result.get('link', '')}\n"
                            f"Snippet: {result.get('snippet', '')}\n"
                            for result in organic_results[:2]
                        ])
                        if formatted_results:
                            news_items.append(formatted_results)
                            logger.debug("Found news from %s", source)
                except Exception as e:
                    logger.warning("Failed to get news from %s: %s", source, str(e))
                    continue

            logger.info("Found %d news items", len(news_items))
            return news_items[:5]  # Return top 5 recent news items

        except Exception as e:
            logger.error("Error gathering MongoDB news: %s", str(e))
            return []