from crewai import Agent
from config.logging_config import setup_logging

logger = setup_logging(__name__)

class WriterAgent:
    @staticmethod
    def create() -> Agent:
        logger.info("Creating WriterAgent")
        agent = Agent(
            role='Technical Blog Writer',
            goal='Write engaging and informative technical blog posts about MongoDB',
            backstory="""You are a skilled technical writer who specializes in creating
            clear, engaging content about complex database technologies. You have a
            knack for making technical concepts accessible while maintaining accuracy.
            You write in a professional yet fun and conversational tone and know how to
            incorporate technical details effectively.""",
            verbose=True,
            allow_delegation=False,
            memory=True,
            max_iter=3,
            llm_config={
                "temperature": 0,
                "request_timeout": 180
            }
        )
        logger.info("WriterAgent created successfully")
        return agent

    @staticmethod
    def create_task_prompt(outline, research):
        logger.info("Creating writing task prompt")
        logger.debug("Outline length: %d characters", len(outline))
        logger.debug("Research length: %d characters", len(research))

        prompt = f"""Write a comprehensive technical blog post based on the following outline
        and research:

        OUTLINE:
        {outline}

        RESEARCH:
        {research}

        Requirements:
        1. Write in a professional but engaging tone
        2. Include appropriate emojis and formatting to enhance readability
        3. Incorporate code examples with proper markdown formatting
        4. Use technical terms accurately but explain them clearly
        5. Total length should be 1500-2000 words
        6. Include a brief introduction and conclusion
        7. Break up text with appropriate headings and subheadings
        8. Add relevant emoji icons at section headings
        9. Include practical tips and real-world applications
        10. Format the entire post in markdown

        The final blog should be technically accurate while being accessible to
        developers with basic MongoDB knowledge. Make complex concepts clear through
        analogies and examples where appropriate."""

        logger.info("Writing task prompt created successfully")
        return prompt