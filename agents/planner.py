from crewai import Agent
from tools.web_tools import WebSearchTools
from config.logging_config import setup_logging

logger = setup_logging(__name__)

class PlannerAgent:
    @staticmethod
    def create() -> Agent:
        logger.info("Creating PlannerAgent")
        agent = Agent(
            role='Technical Blog Planner',
            goal='Plan and outline compelling technical blog posts about MongoDB',
            backstory="""You are an experienced technical blog planner with deep knowledge
            of MongoDB and database technologies. You stay up-to-date with the latest
            MongoDB developments and know how to structure content for maximum engagement.""",
            tools=[WebSearchTools.search_web()],
            verbose=True,
            allow_delegation=False,
            memory=True,
            max_iter=3,
            llm_config={
                "temperature": 0.7,
                "request_timeout": 120
            }
        )
        logger.info("PlannerAgent created successfully")
        return agent

    @staticmethod
    def create_task_prompt(topic=None):
        logger.info("Creating task prompt with topic: %s", topic if topic else "AI-chosen topic")
        
        if topic:
            prompt = f"""Analyze and create a detailed blog post outline about {topic} in MongoDB.
            If the topic is not specific enough, focus on the most recent and relevant aspect of it.

            1. Research the latest developments, updates, and best practices about this topic
            2. Create a compelling outline with:
               - An attention-grabbing title
               - 4-6 main sections
               - Key points to cover in each section
               - Suggestions for code examples or diagrams
               - Target word count for each section

            Format the outline in markdown with clear hierarchical structure.
            Include relevant technical terms and concepts to be covered.
            """
            logger.debug("Created topic-specific prompt")
        else:
            prompt = """Research and identify a cutting-edge MongoDB topic for a technical blog post.
            Focus on recent developments, new features, or innovative use cases.

            1. Search for recent MongoDB news, releases, and discussions
            2. Identify 2-3 potential topics and select the most promising one
            3. Create a detailed outline following this structure:
               - Attention-grabbing title
               - 4-6 main sections
               - Key points to cover in each section
               - Suggestions for code examples or diagrams
               - Target word count for each section

            Format the outline in markdown with clear hierarchical structure.
            The total blog length should be 1500-2000 words.
            Include relevant technical terms and concepts to be covered.
            """
            logger.debug("Created AI-chosen topic prompt")
        
        logger.info("Task prompt created successfully")
        return prompt