"""
MongoDB Blog Generator
A CrewAI-powered system for generating technical blog posts about MongoDB
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .agents import PlannerAgent, ResearcherAgent, WriterAgent, EditorAgent
from .crew import BlogCrew

__all__ = [
    'PlannerAgent',
    'ResearcherAgent',
    'WriterAgent',
    'EditorAgent',
    'BlogCrew'
]