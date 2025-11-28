"""AI Spark Performance Coach - Analyze Spark event logs and get AI-powered performance insights."""

__version__ = "0.1.0"

from .spark_log_parser import SparkLogParser
from .rules import PerformanceRules
from .ai_coach import AICoach
from .cli import main

__all__ = ["SparkLogParser", "PerformanceRules", "AICoach", "main"]

