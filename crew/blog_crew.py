from pickle import TRUE
from crewai import Crew, Task
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from agents.editor import EditorAgent
from config.logging_config import setup_logging
import os
import traceback

logger = setup_logging(__name__)

class BlogCrew:
    def __init__(self, topic=None):
        logger.info("Initializing BlogCrew with topic: %s", topic if topic else "AI-chosen topic")
        self.topic = topic

        logger.debug("Creating agents...")
        self.planner = PlannerAgent.create()
        self.researcher = ResearcherAgent.create()
        self.writer = WriterAgent.create()
        self.editor = EditorAgent.create()
        logger.info("All agents created successfully")

    def create_tasks(self):
        logger.info("Creating blog generation tasks")

        # Task 1: Planning
        logger.debug("Creating planning task")
        planning_task = Task(
            description=PlannerAgent.create_task_prompt(self.topic),
            agent=self.planner,
            expected_output="Detailed blog outline in markdown format",
            output_file="blog_outline.md",
            context=None
        )
        logger.info("Planning task created successfully")
        logger.debug("Planning task output: %s", planning_task.output_file)

        # Task 2: Research
        logger.debug("Creating research task")
        research_task = Task(
            description=ResearcherAgent.create_task_prompt(planning_task.output_file),
            agent=self.researcher,
            expected_output="Comprehensive research content in markdown format",
            output_file="research_content.md",
            context=[planning_task]
        )

        # Task 3: Writing
        logger.debug("Creating writing task")
        writing_task = Task(
            description=WriterAgent.create_task_prompt(
                planning_task.output_file,
                research_task.output_file
            ),
            agent=self.writer,
            expected_output="Draft of the blog post in markdown format",
            output_file="blog_draft.md",
            context=[planning_task, research_task]
        )

        # Task 4: Editing
        logger.debug("Creating editing task")
        editing_task = Task(
            description=EditorAgent.create_task_prompt(
                writing_task.output_file,
                self.extract_title(planning_task.output_file)
            ),
            agent=self.editor,
            expected_output="Finalized blog post in markdown format",
            output_file="final_blog.md",
            context=[writing_task]
        )

        tasks = [planning_task, research_task, writing_task, editing_task]
        logger.info("Created %d tasks successfully", len(tasks))
        return tasks

    def run(self, callback=None):
        try:
            if callback:
                callback("Creating blog generation tasks...", 0.15)
            tasks = self.create_tasks()

            crew = Crew(
                agents=[self.planner, self.researcher, self.writer, self.editor],
                tasks=tasks,
            )

            if callback:
                callback("Starting crew tasks execution...", 0.30)
            logger.info("Kicking off crew tasks")
            result = crew.kickoff()

            # Save the final blog
            if callback:
                callback("Finalizing and saving blog...", 0.95)
                logger.debug("Callback executed: Saving final blog")

            title = self.extract_title(str(result))  # Convert CrewOutput to string
            logger.info("Extracted blog title: %s", title)

            filepath = EditorAgent.save_blog(result, title)
            logger.info("Blog saved successfully at: %s", filepath)

            return filepath

        except Exception as e:
            logger.error("Error in blog creation process: %s", str(e))
            if callback:
                callback(f"Error occurred: {str(e)}", 1.0)
            traceback.print_exc()
            raise

    @staticmethod
    def extract_title(content):
        """Extract the blog title from the content"""
        logger.debug("Extracting title from content")
        try:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    title = line.replace('# ', '')
                    logger.debug("Found title with '# ': %s", title)
                    return title
                elif line.startswith('#'):
                    title = line.replace('#', '')
                    logger.debug("Found title with '#': %s", title)
                    return title

            default_title = "MongoDB Technical Blog"
            logger.debug("No title found, using default: %s", default_title)
            return default_title

        except Exception as e:
            logger.error("Error extracting title: %s", str(e))
            return "MongoDB Technical Blog"

    @staticmethod
    def list_blogs():
        """List all generated blogs"""
        logger.info("Listing all generated blogs")

        blogs_dir = os.path.join('data', 'blogs')
        if not os.path.exists(blogs_dir):
            logger.debug("Blogs directory does not exist: %s", blogs_dir)
            return []

        try:
            blog_files = [
                os.path.join(blogs_dir, f)
                for f in os.listdir(blogs_dir)
                if f.endswith('.md')
            ]
            logger.info("Found %d blog files", len(blog_files))
            return blog_files

        except Exception as e:
            logger.error("Error listing blogs: %s", str(e))
            return []