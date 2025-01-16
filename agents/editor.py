from crewai import Agent
import os
from datetime import datetime
import frontmatter
from config.logging_config import setup_logging

logger = setup_logging(__name__)

class EditorAgent:
    @staticmethod
    def create() -> Agent:
        logger.info("Creating EditorAgent")
        agent = Agent(
            role='Technical Content Editor',
            goal='Ensure technical blog posts are accurate, well-written, and properly formatted',
            backstory="""You are a meticulous editor with extensive experience in
            technical content. You have a sharp eye for detail, strong command of
            English grammar, and deep understanding of technical writing best
            practices. You ensure content is not only accurate but also engaging
            and accessible.""",
            verbose=True,
            allow_delegation=False,
            memory=True,
            max_iter=2,
            llm_config={
                "temperature": 0.4,
                "request_timeout": 120
            }
        )
        logger.info("EditorAgent created successfully")
        return agent

    @staticmethod
    def create_task_prompt(blog_content, title):
        logger.info("Creating editing task prompt for title: %s", title)
        logger.debug("Blog content length: %d characters", len(blog_content))
        
        prompt = f"""Review and edit the following technical blog post:

        {blog_content}

        Tasks:
        1. Check for technical accuracy and clarity
        2. Ensure proper grammar, spelling, and punctuation
        3. Verify markdown formatting is correct
        4. Confirm appropriate use of emojis and formatting
        5. Check code examples for correctness
        6. Ensure consistent tone and style
        7. Verify section flow and logical progression
        8. Check word count (target: 1500-2000 words)
        9. Add metadata including:
           - Title: {title}
           - Date: {datetime.now().strftime('%Y-%m-%d')}
           - Tags: [appropriately selected based on content]
           - Description: [brief summary]

        Save the final version with proper frontmatter in markdown format.
        Return the edited content with a summary of major changes made."""
        
        logger.info("Editing task prompt created successfully")
        return prompt

    @staticmethod
    def save_blog(content, title):
        """Save the blog post with proper frontmatter"""
        logger.info("Saving blog post with title: %s", title)
        
        try:
            # Create blogs directory if it doesn't exist
            blogs_dir = os.path.join('data', 'blogs')
            os.makedirs(blogs_dir, exist_ok=True)
            logger.debug("Created blogs directory: %s", blogs_dir)

            # Create metadata
            content_str = str(content)  # Convert CrewOutput to string
            metadata = {
                'title': title,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'tags': ['mongodb', 'databases', 'technical'],
                'description': ' '.join(content_str.split('\n')[0:2])  # First two lines as description
            }
            logger.debug("Created metadata: %s", metadata)

            # Create post with frontmatter
            post = frontmatter.Post(content_str, **metadata)

            # Generate filename from title
            filename = title.lower().replace(' ', '-').replace('/', '-') + '.md'
            filepath = os.path.join(blogs_dir, filename)
            logger.debug("Generated filepath: %s", filepath)

            # Save the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            logger.info("Blog post saved successfully at: %s", filepath)
            return filepath
            
        except Exception as e:
            logger.error("Error saving blog post: %s", str(e))
            raise