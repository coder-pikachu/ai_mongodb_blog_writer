from crewai import Agent
from tools.web_tools import WebSearchTools
from config.logging_config import setup_logging

logger = setup_logging(__name__)

class ResearcherAgent:
    @staticmethod
    def create() -> Agent:
        logger.info("Creating ResearcherAgent")
        agent = Agent(
            role='Technical Content Researcher',
            goal='Research and gather comprehensive information about MongoDB topics',
            backstory="""You are a meticulous technical researcher with expertise in
            database technologies who uses search and web scraping tools. You excel at finding, validating, and synthesizing
            technical information from multiple sources. You understand MongoDB deeply
            and can evaluate the credibility of technical content.
            Be smart on using the tools and don't overuse the tools keeping maximum 3-4 requests in a minute.
            """,
            tools=[
                WebSearchTools.search_web(),
                WebSearchTools.scrape_web()
            ],
            verbose=True,
            allow_delegation=False,
            memory=True,
            max_iter=10,
            llm_config={
                "temperature": 0.3,
                "request_timeout": 300
            }
        )
        logger.info("ResearcherAgent created successfully with %d tools", len(agent.tools))
        return agent

    @staticmethod
    def create_task_prompt(outline):
        logger.info("Creating research task prompt")
        logger.debug("Outline length: %d characters", len(outline))

        prompt = f"""Research and gather detailed information based on the following blog outline:

        {outline}

        For each section in the outline:
        1. Find relevant technical documentation, articles, and real-world examples
        2. Gather specific code examples, configuration snippets, or architectural diagrams
        3. Identify key statistics, benchmarks, or performance metrics if applicable
        4. Look for expert opinions, best practices, and common pitfalls
        5. Find recent updates or changes related to each topic

        Compile your research in a structured markdown format with:
        - Source citations for each piece of information making sure those links are active
        - Direct quotes where appropriate
        - Technical specifications and version details
        - Active and working links to official documentation or reliable sources

        Focus on accuracy and technical depth while ensuring the information is
        recent and relevant."""

        logger.info("Research task prompt created successfully")
        return prompt