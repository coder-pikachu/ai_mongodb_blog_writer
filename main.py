from mesop import component as c
from mesop.events import Event
from mesop.components.text_field import TextFieldChangeEvent
from mesop.components.button import ButtonClickEvent
from crew.blog_crew import BlogCrew
import frontmatter
from datetime import datetime
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('blog_generator.log')
    ]
)
logger = logging.getLogger(__name__)

# State management
class State:
    def __init__(self):
        self.topic = ""
        self.keywords = ""
        self.blogs = []
        self.current_blog = None
        self.generating = False

state = State()

def load_blog_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        post = frontmatter.load(file)
        return post.metadata, post.content

def handle_topic_change(event: TextFieldChangeEvent):
    state.topic = event.value

def handle_keywords_change(event: TextFieldChangeEvent):
    state.keywords = event.value

def create_blog():
    if not state.topic or not state.keywords:
        return c.text("Please enter both topic and keywords")
    
    state.generating = True
    blog_crew = BlogCrew()
    
    try:
        blog_content = blog_crew.generate_blog_post(state.topic, state.keywords)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{state.topic.lower().replace(' ', '_')}.md"
        filepath = os.path.join("data/blogs", filename)
        
        os.makedirs("data/blogs", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(blog_content)
            
        state.generating = False
        return c.text("Blog created successfully!")
    except Exception as e:
        state.generating = False
        logger.error(f"Error generating blog: {str(e)}")
        return c.text(f"Error: {str(e)}")

def view_blogs():
    blogs_dir = "data/blogs"
    if not os.path.exists(blogs_dir):
        return c.text("No blogs found")
        
    blog_files = [f for f in os.listdir(blogs_dir) if f.endswith('.md')]
    blog_contents = []
    
    for file in blog_files:
        filepath = os.path.join(blogs_dir, file)
        metadata, content = load_blog_content(filepath)
        blog_contents.append(
            c.card(
                c.column([
                    c.text(f"Title: {metadata.get('title', 'Untitled')}"),
                    c.text(f"Author: {metadata.get('author', 'Unknown')}"),
                    c.text(f"Date: {metadata.get('date', 'Unknown')}"),
                    c.text(f"Keywords: {', '.join(metadata.get('keywords', []))}"),
                    c.text("Content Preview:"),
                    c.text(content[:200] + "...")
                ])
            )
        )
    
    return c.column(blog_contents)

def app():
    return c.column([
        c.app_bar(c.text("MongoDB Blog Generator", variant="h4")),
        c.container([
            c.card(
                c.column([
                    c.text("Create New Blog", variant="h5"),
                    c.text_field(
                        label="Blog Topic",
                        on_change=handle_topic_change,
                        value=state.topic
                    ),
                    c.text_field(
                        label="Keywords (comma-separated)",
                        on_change=handle_keywords_change,
                        value=state.keywords
                    ),
                    c.button(
                        "Generate Blog",
                        on_click=lambda _: create_blog(),
                        disabled=state.generating
                    ),
                    c.progress_linear() if state.generating else None,
                ])
            ),
            c.divider(),
            c.text("Generated Blogs", variant="h5"),
            view_blogs()
        ])
    ])

if __name__ == "__main__":
    from mesop import run
    run(app)
