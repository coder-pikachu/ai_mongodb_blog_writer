import streamlit as st
import os
from crew.blog_crew import BlogCrew
import frontmatter
from datetime import datetime
import time
import logging
import sys

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

# Streamlit configuration
st.set_page_config(
    page_title="MongoDB Blog Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""

""", unsafe_allow_html=True)

def load_blog_content(filepath):
    """Load blog content with frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        return post.metadata, post.content

def display_blog_preview(metadata, content):
    """Display blog preview with metadata"""
    logger.info("Displaying blog preview with metadata: %s", metadata.get('title', 'Untitled'))

    st.markdown("### 📑 Blog Preview")

    # Create a container for the preview
    preview_container = st.container()
    with preview_container:
        # Display metadata in an organized way
        st.markdown("#### 📋 Metadata")
        metadata_container = st.container()
        with metadata_container:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Title:** {metadata.get('title', 'Untitled')}")
                st.markdown(f"**Date:** {metadata.get('date', 'No date')}")
                st.markdown(f"**Author:** {metadata.get('author', 'AI Generated')}")
            with col2:
                st.markdown(f"**Tags:** {', '.join(metadata.get('tags', []))}")
                if 'category' in metadata:
                    st.markdown(f"**Category:** {metadata['category']}")

        if 'description' in metadata:
            st.markdown("#### 📝 Description")
            st.info(metadata['description'])

        # Display content with proper formatting
        st.markdown("#### 📖 Content")
        st.markdown("---")
        st.markdown(content)
        st.markdown("---")

def create_blog():
    logger.info("Entering create_blog function")
    st.markdown("### ✨ Create New Blog")

    # Topic input with better UI
    topic = st.text_input(
        "Enter a specific MongoDB topic (optional)",
        placeholder="Leave empty for AI to choose a trending topic",
        help="You can specify a particular MongoDB topic or let AI choose a trending one"
    )

    # Add some example topics as chips
    st.markdown("##### 💡 Example topics:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("- MongoDB Aggregation Pipeline")
    with col2:
        st.markdown("- MongoDB Atlas Search")
    with col3:
        st.markdown("- MongoDB Time Series Collections")

    if st.button("🚀 Generate Blog", use_container_width=True):
        logger.info("Starting blog generation process with topic: %s", topic if topic else "AI-chosen topic")

        # Create containers for progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            details_expander = st.expander("View detailed progress", expanded=True)

        def update_progress(message, progress=None):
            """Update progress with more detailed logging"""
            status_text.markdown(f"<div class='status-text'>{message}</div>", unsafe_allow_html=True)
            if progress is not None:
                progress_bar.progress(progress)
            with details_expander:
                st.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
            logger.info(message)

        try:
            # Create and run crew with enhanced progress tracking
            update_progress("🎯 Initializing blog generation process...", 0.1)
            crew = BlogCrew(topic)
            update_progress("🤔 Analyzing topic and planning blog structure...", 0.25)
            update_progress("📚 Researching MongoDB documentation and best practices...", 0.40)
            update_progress("✍️ Writing blog draft with technical insights...", 0.60)
            update_progress("🔍 Reviewing technical accuracy and code examples...", 0.75)
            update_progress("✨ Polishing content and formatting...", 0.90)
            filepath = crew.run(callback=update_progress)
            update_progress("✅ Blog generated successfully!", 1.0)
            logger.info("Blog generation completed. File saved at: %s", filepath)

            # Load and display the generated blog
            try:
                metadata, content = load_blog_content(filepath)
                display_blog_preview(metadata, content)
            except Exception as e:
                logger.error("Error loading blog content: %s", str(e))
                st.error("Blog was generated but there was an error displaying it. Please check the logs.")

        except Exception as e:
            error_msg = f"Error generating blog: {str(e)}"
            logger.error(error_msg, exc_info=True)
            st.error(error_msg)
            with details_expander:
                st.error("Detailed error information has been logged. Check blog_generator.log for more details.")
            progress_bar.empty()
            status_text.empty()

def view_blogs():
    logger.info("Entering view_blogs function")
    st.markdown("### 📚 Existing Blogs")

    try:
        # Get list of blogs
        blogs = BlogCrew.list_blogs()
        logger.info("Found %d existing blogs", len(blogs))

        if not blogs:
            st.info("🎉 No blogs generated yet. Create your first blog!")
            return

        # Create selection for blogs with better organization
        blog_titles = []
        blog_dict = {}

        for blog_path in blogs:
            try:
                metadata, _ = load_blog_content(blog_path)
                title = metadata.get('title', os.path.basename(blog_path))
                date = metadata.get('date', 'No date')
                display_title = f"{title} ({date})"
                blog_titles.append(display_title)
                blog_dict[display_title] = blog_path
            except Exception as e:
                logger.error("Error loading blog at %s: %s", blog_path, str(e))
                continue

        selected_blog = st.selectbox(
            "📖 Select a blog to view",
            blog_titles,
            help="Choose a blog from the list to view its contents"
        )

        if selected_blog:
            logger.info("Displaying blog: %s", selected_blog)
            try:
                metadata, content = load_blog_content(blog_dict[selected_blog])
                display_blog_preview(metadata, content)
            except Exception as e:
                logger.error("Error displaying blog %s: %s", selected_blog, str(e))
                st.error(f"Error displaying blog: {str(e)}")

    except Exception as e:
        logger.error("Error in view_blogs: %s", str(e))
        st.error(f"Error loading blogs: {str(e)}")

def main():
    logger.info("Starting MongoDB Blog Generator application")

    # Application header with improved styling
    st.title("📝 MongoDB Blog Generator")
    st.markdown("""
    <div style='background-color: #000; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
        <h4>Generate insightful technical blog posts about MongoDB using AI</h4>
        <p>Choose to create a new blog or view existing ones. Our AI will help you create detailed,
        technically accurate content about MongoDB topics.</p>
    </div>
    """, unsafe_allow_html=True)

    # Create tabs with icons
    tab1, tab2 = st.tabs(["✨ Create New Blog", "📚 View Existing Blogs"])

    with tab1:
        create_blog()

    with tab2:
        view_blogs()

    # Add footer
    st.markdown("---")
    st.markdown("""
        <div class='footer'>
            <p>MongoDB Blog Generator • Powered by AI</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()