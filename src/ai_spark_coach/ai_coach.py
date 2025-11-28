"""AI-powered performance coach that generates insights and recommendations."""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .rules import PerformanceIssue


class AICoach:
    """Generate AI-powered performance insights and recommendations."""
    
    def __init__(
        self,
        use_llm: bool = True,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize AI Coach.
        
        Args:
            use_llm: Whether to use LLM for recommendations (default: True)
            api_key: API key for OpenAI (optional, will try to load from .env or OPENAI_API_KEY env var)
            model: OpenAI model to use (default: "gpt-4o-mini")
        """
        self.use_llm = use_llm
        self.model = model
        
        # Load .env file if python-dotenv is available
        if load_dotenv:
            # Try multiple locations for .env file
            # 1. Current working directory (most common)
            # 2. Same directory as this file (src/ai_spark_coach/)
            # 3. src directory
            # 4. Project root (where package is installed)
            # 5. User's home directory
            env_paths = [
                Path.cwd() / ".env",  # Current working directory
                Path(__file__).parent / ".env",  # Same directory as ai_coach.py (src/ai_spark_coach/)
                Path(__file__).parent.parent / ".env",  # src directory
                Path(__file__).parent.parent.parent / ".env",  # Project root
                Path.home() / ".env",  # Home directory
            ]
            
            # Try to load .env from any of these locations
            env_loaded = False
            for env_path in env_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=False)  # Don't override existing env vars
                    env_loaded = True
                    break
            
            # If no .env file found in specific paths, try default behavior
            # (searches current directory and parent directories)
            if not env_loaded:
                load_dotenv(override=False)
        else:
            # If python-dotenv is not installed, warn but continue
            if use_llm:
                print("Note: python-dotenv not installed. .env file won't be loaded automatically.")
                print("Install with: pip install python-dotenv")
        
        # Get API key from parameter, environment variable, or .env file
        # Priority: 1. api_key parameter, 2. Environment variable, 3. .env file (already loaded)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if self.use_llm and self.api_key:
            if not OPENAI_AVAILABLE:
                print("Warning: OpenAI package not installed. Install with: pip install openai")
                print("Falling back to rule-based recommendations.")
                self.use_llm = False
            else:
                try:
                    self.openai_client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    print(f"Warning: Failed to initialize OpenAI client: {e}")
                    print("Falling back to rule-based recommendations.")
                    self.use_llm = False
        elif self.use_llm and not self.api_key:
            print("Warning: OPENAI_API_KEY not found.")
            print("  - Create a .env file in the project root with: OPENAI_API_KEY=your-key")
            print("  - Or set environment variable: export OPENAI_API_KEY=your-key")
            print("  - Or pass via CLI: --api-key your-key")
            print("Falling back to rule-based recommendations.")
            self.use_llm = False
    
    def generate_report(
        self,
        summary: Dict[str, Any],
        issues: List[PerformanceIssue]
    ) -> str:
        """
        Generate a human-readable performance report.
        
        Args:
            summary: Summary from SparkLogParser
            issues: List of detected performance issues
            
        Returns:
            Formatted report string
        """
        report_parts = []
        
        # Summary section
        report_parts.append("=" * 70)
        report_parts.append("SPARK PERFORMANCE ANALYSIS")
        report_parts.append("=" * 70)
        report_parts.append("")
        
        report_parts.append(f"Total Jobs: {summary.get('num_jobs', 0)}")
        report_parts.append(f"Total Stages: {summary.get('num_stages', 0)}")
        report_parts.append(f"Total Duration: {summary.get('total_duration', 0):.1f}s")
        report_parts.append("")
        
        # Stage breakdown
        report_parts.append("STAGE BREAKDOWN:")
        report_parts.append("-" * 70)
        stages = summary.get("stages", [])
        total_duration = summary.get("total_duration", 1.0)
        
        for stage in stages:
            stage_id = stage["stage_id"]
            stage_name = stage.get("stage_name", f"Stage {stage_id}")
            duration = stage.get("total_duration", 0)
            percentage = (duration / total_duration * 100) if total_duration > 0 else 0
            shuffle_mb = stage.get("shuffle_read_size_mb", 0)
            
            report_parts.append(
                f"Stage {stage_id}: {stage_name}"
            )
            report_parts.append(
                f"  Duration: {duration:.1f}s ({percentage:.0f}% of total)"
            )
            report_parts.append(
                f"  Tasks: {stage.get('num_tasks', 0)}"
            )
            if shuffle_mb > 0:
                report_parts.append(
                    f"  Shuffle Read: {shuffle_mb:.1f} MB"
                )
            report_parts.append("")
        
        # Issues section
        if issues:
            report_parts.append("=" * 70)
            report_parts.append("DETECTED ISSUES")
            report_parts.append("=" * 70)
            report_parts.append("")
            
            # Group by severity
            high_issues = [i for i in issues if i.severity == "high"]
            medium_issues = [i for i in issues if i.severity == "medium"]
            low_issues = [i for i in issues if i.severity == "low"]
            
            if high_issues:
                report_parts.append("HIGH SEVERITY:")
                for issue in high_issues:
                    report_parts.append(f"  ⚠️  {issue.description}")
                report_parts.append("")
            
            if medium_issues:
                report_parts.append("MEDIUM SEVERITY:")
                for issue in medium_issues:
                    report_parts.append(f"  ⚠️  {issue.description}")
                report_parts.append("")
            
            if low_issues:
                report_parts.append("LOW SEVERITY:")
                for issue in low_issues:
                    report_parts.append(f"  ⚠️  {issue.description}")
                report_parts.append("")
        
        # Recommendations
        report_parts.append("=" * 70)
        report_parts.append("RECOMMENDATIONS")
        report_parts.append("=" * 70)
        report_parts.append("")
        
        if self.use_llm:
            recommendations = self._generate_llm_recommendations(summary, issues)
        else:
            recommendations = self._generate_rule_based_recommendations(issues)
        
        report_parts.append(recommendations)
        report_parts.append("")
        
        return "\n".join(report_parts)
    
    def _generate_rule_based_recommendations(self, issues: List[PerformanceIssue]) -> str:
        """Generate recommendations based on rules (fallback when LLM not available)."""
        recommendations = []
        
        for issue in issues:
            if issue.issue_type == "task_skew":
                recommendations.append(
                    f"Stage {issue.stage_id} - Task Skew:\n"
                    f"  • Consider repartitioning on a different key\n"
                    f"  • Use salting technique to distribute skewed keys\n"
                    f"  • Check for data skew in join keys or groupBy columns"
                )
            elif issue.issue_type == "large_shuffle":
                shuffle_mb = issue.metrics.get("shuffle_read_mb", 0)
                recommendations.append(
                    f"Stage {issue.stage_id} - Large Shuffle ({shuffle_mb:.1f} MB):\n"
                    f"  • Consider using broadcast join if one table is small (< 2GB)\n"
                    f"  • Repartition before the join to reduce shuffle size\n"
                    f"  • Check if join keys are properly distributed\n"
                    f"  • Consider using bucketing for frequently joined tables"
                )
            elif issue.issue_type == "long_stage":
                percentage = issue.metrics.get("percentage", 0)
                recommendations.append(
                    f"Stage {issue.stage_id} - Long Running ({percentage:.0f}% of total time):\n"
                    f"  • Review the operations in this stage\n"
                    f"  • Check for unnecessary data scans\n"
                    f"  • Consider caching intermediate results if reused"
                )
        
        if not recommendations:
            return "No specific recommendations. Your Spark job appears to be well-optimized!"
        
        return "\n\n".join(recommendations)
    
    def _generate_llm_recommendations(
        self,
        summary: Dict[str, Any],
        issues: List[PerformanceIssue]
    ) -> str:
        """
        Generate recommendations using OpenAI LLM.
        
        Args:
            summary: Summary from SparkLogParser
            issues: List of detected performance issues
            
        Returns:
            AI-generated recommendations string
        """
        if not self.openai_client:
            # Fall back to rule-based if OpenAI is not available
            return self._generate_rule_based_recommendations(issues)
        
        # Build prompt
        prompt = self._build_prompt(summary, issues)
        
        try:
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert Apache Spark performance engineer. "
                            "Analyze Spark job performance metrics and provide specific, "
                            "actionable tuning recommendations. Focus on the most impactful "
                            "optimizations first. Be concise but thorough."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more focused, technical responses
                max_tokens=1000
            )
            
            recommendations = response.choices[0].message.content.strip()
            return recommendations
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            print("Falling back to rule-based recommendations.")
            return self._generate_rule_based_recommendations(issues)
    
    def _build_prompt(self, summary: Dict[str, Any], issues: List[PerformanceIssue]) -> str:
        """Build a prompt for the LLM."""
        prompt_parts = [
            "Analyze this Spark job performance and provide specific tuning recommendations:",
            "",
            f"Total Duration: {summary.get('total_duration', 0):.1f}s",
            f"Stages: {summary.get('num_stages', 0)}",
            "",
            "Stage Details:"
        ]
        
        for stage in summary.get("stages", []):
            prompt_parts.append(
                f"  Stage {stage['stage_id']}: {stage.get('stage_name', '')} - "
                f"{stage.get('total_duration', 0):.1f}s, "
                f"{stage.get('num_tasks', 0)} tasks, "
                f"shuffle: {stage.get('shuffle_read_size_mb', 0):.1f} MB"
            )
        
        if issues:
            prompt_parts.append("")
            prompt_parts.append("Detected Issues:")
            for issue in issues:
                prompt_parts.append(f"  - {issue.description}")
        
        prompt_parts.append("")
        prompt_parts.append(
            "Provide specific, actionable recommendations to improve performance. "
            "Focus on the most impactful changes first."
        )
        
        return "\n".join(prompt_parts)

