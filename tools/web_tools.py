from langchain.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from config.logging_config import setup_logging

import requests
from bs4 import BeautifulSoup
from typing import Optional, List
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

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
            search = GoogleSearchAPIWrapper(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                google_cse_id=os.getenv("GOOGLE_CSE_ID")
            )
            logger.debug("Google Search API initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Google Search API: %s", str(e))
            raise

        def enhanced_search(query: str) -> str:
            """Enhanced search with source prioritization"""
            logger.info("Performing enhanced search for query: %s", query)
            
            # Search priority sources first
            priority_results = []
            for source in WebSearchTools.PRIORITY_SOURCES:
                source_query = f"{query} site:{source}"
                try:
                    logger.debug("Searching priority source: %s", source)
                    results = search.run(source_query)
                    if results:
                        priority_results.append(results)
                        logger.debug("Found results from %s", source)
                except Exception as e:
                    logger.warning("Failed to search %s: %s", source, str(e))
                    continue

            # Search tech sources
            tech_results = []
            for source in WebSearchTools.TECH_SOURCES:
                source_query = f"{query} site:{source}"
                try:
                    logger.debug("Searching tech source: %s", source)
                    results = search.run(source_query)
                    if results:
                        tech_results.append(results)
                        logger.debug("Found results from %s", source)
                except Exception as e:
                    logger.warning("Failed to search %s: %s", source, str(e))
                    continue

            # Combine results with priority order
            combined_results = "\n\nPriority Sources:\n" + "\n".join(priority_results[:3])
            combined_results += "\n\nTechnical Sources:\n" + "\n".join(tech_results[:2])

            # Add general search results
            try:
                logger.debug("Performing general search")
                general_results = search.run(f"{query} mongodb recent")
                combined_results += "\n\nAdditional Sources:\n" + general_results
            except Exception as e:
                logger.warning("Failed to perform general search: %s", str(e))

            logger.info("Search completed successfully")
            return combined_results

        return Tool(
            name="Search",
            func=enhanced_search,
            description="""
            Advanced search tool for MongoDB information. Prioritizes official documentation,
            MongoDB blog posts, and trusted technical sources. Use specific queries for best results.
            """
        )

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
            search = GoogleSearchAPIWrapper(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                google_cse_id=os.getenv("GOOGLE_CSE_ID")
            )
            logger.debug("Google Search API initialized for news gathering")

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
                    if results:
                        news_items.append(results)
                        logger.debug("Found news from %s", source)
                except Exception as e:
                    logger.warning("Failed to get news from %s: %s", source, str(e))
                    continue

            logger.info("Found %d news items", len(news_items))
            return news_items[:5]  # Return top 5 recent news items
            
        except Exception as e:
            logger.error("Error gathering MongoDB news: %s", str(e))
            return []