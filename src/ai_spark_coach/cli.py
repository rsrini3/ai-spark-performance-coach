"""Command-line interface for AI Spark Performance Coach."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .spark_log_parser import SparkLogParser
from .rules import PerformanceRules
from .ai_coach import AICoach


def main(args: Optional[list] = None):
    """
    Main CLI entry point.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
    """
    parser = argparse.ArgumentParser(
        description="AI Spark Performance Coach - Analyze Spark event logs and get performance insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --event-log /tmp/spark-events/app-20251128-0001
  %(prog)s --event-log /path/to/log.gz --no-llm
  %(prog)s --event-log /path/to/log --output report.txt
        """
    )
    
    parser.add_argument(
        "--event-log",
        required=True,
        type=str,
        help="Path to Spark event log file (supports .gz files)"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM recommendations (use rule-based only)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY in .env file or environment variable)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Write report to file instead of stdout"
    )
    
    parsed_args = parser.parse_args(args)
    
    # Validate event log path
    event_log_path = Path(parsed_args.event_log)
    if not event_log_path.exists():
        print(f"Error: Event log not found: {parsed_args.event_log}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse event log
        print("Parsing Spark event log...", file=sys.stderr)
        parser_obj = SparkLogParser(str(event_log_path))
        summary = parser_obj.parse()
        
        # Detect issues
        print("Analyzing performance...", file=sys.stderr)
        issues = PerformanceRules.analyze(summary)
        
        # Generate report
        print("Generating report...", file=sys.stderr)
        coach = AICoach(
            use_llm=not parsed_args.no_llm,
            api_key=parsed_args.api_key,
            model=parsed_args.model
        )
        report = coach.generate_report(summary, issues)
        
        # Output report
        if parsed_args.output:
            output_path = Path(parsed_args.output)
            output_path.write_text(report)
            print(f"Report written to: {output_path}", file=sys.stderr)
        else:
            print(report)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

