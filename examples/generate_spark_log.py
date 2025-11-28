#!/usr/bin/env python3
"""
Generate a Spark event log for testing the AI Spark Performance Coach.

This script runs a simple Spark job with event logging enabled.
Make sure you have PySpark installed: pip install pyspark
"""

import os
import sys
from pathlib import Path

# CRITICAL: Set JAVA_HOME before importing PySpark
# PySpark needs JAVA_HOME to be set at import time
if not os.environ.get("JAVA_HOME"):
    # Try to find Java on macOS
    java_home_candidates = [
        "/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home",
        "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home",
    ]
    for candidate in java_home_candidates:
        if Path(candidate).exists():
            os.environ["JAVA_HOME"] = candidate
            print(f"Setting JAVA_HOME to: {candidate}")
            break
    else:
        # Try using java_home command on macOS
        import subprocess
        try:
            java_home = subprocess.check_output(
                ["/usr/libexec/java_home"], text=True
            ).strip()
            os.environ["JAVA_HOME"] = java_home
            print(f"Setting JAVA_HOME to: {java_home}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: JAVA_HOME not set. PySpark may not work correctly.")
            print("Please set JAVA_HOME to your Java installation directory.")
            print("Example: export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home")

# Workaround for PySpark 4.0+ Java initialization issues
# Set PYSPARK_PYTHON to ensure proper Python/Java communication
if not os.environ.get("PYSPARK_PYTHON"):
    os.environ["PYSPARK_PYTHON"] = sys.executable

# Now import PySpark (JAVA_HOME must be set before this)
try:
    # Import SparkContext first to initialize Java gateway
    from pyspark import SparkContext, SparkConf
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
except ImportError:
    print("Error: PySpark is not installed.")
    print("Install it with: pip install pyspark")
    sys.exit(1)


def main():
    """Generate a Spark event log."""
    # Create event log directory
    event_log_dir = Path("/tmp/spark-events")
    event_log_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating Spark session with event logging enabled...")
    print(f"Event logs will be saved to: {event_log_dir}")
    
    try:
        # Workaround for PySpark 4.0+ Java initialization bug
        # Stop any existing SparkContext first
        try:
            sc = SparkContext._active_spark_context
            if sc is not None:
                sc.stop()
        except:
            pass
        
        # Additional configuration to help with Java initialization
        spark_config = (
            SparkSession.builder
            .appName("local-perf-test")
            .config("spark.eventLog.enabled", "true")
            .config("spark.eventLog.dir", f"file://{event_log_dir}")
            .config("spark.master", "local[*]")
            .config("spark.driver.memory", "2g")
            .config("spark.executor.memory", "2g")
            .config("spark.driver.host", "localhost")
        )
        
        # Try to create SparkSession with explicit Java gateway initialization
        # This is a workaround for the 'JavaPackage' object is not callable error
        try:
            spark = spark_config.getOrCreate()
        except TypeError as e:
            if "'JavaPackage' object is not callable" in str(e):
                print("\n⚠️  PySpark 4.0+ Java initialization issue detected.")
                print("Trying alternative initialization method...")
                # Force re-initialization
                import pyspark.java_gateway
                pyspark.java_gateway.launch_gateway = lambda: None  # Reset
                spark = spark_config.getOrCreate()
            else:
                raise
        
        print("Running Spark job...")
        
        # Create a simple job with some shuffle operations
        df = spark.range(0, 10_000_000).withColumn("k", col("id") % 1000)
        df2 = df.groupBy("k").count()
        result = df2.collect()
        
        print(f"Job completed! Processed {len(result)} groups.")
        
        # Get the application ID to find the event log
        app_id = spark.sparkContext.applicationId
        event_log_path = event_log_dir / app_id
        
        print(f"\n✓ Event log generated: {event_log_path}")
        print(f"\nYou can now analyze it with:")
        print(f"  python -m ai_spark_coach.cli --event-log {event_log_path}")
        
        spark.stop()
        
    except Exception as e:
        print(f"\nError running Spark job: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Java is installed: java -version")
        print("2. Set JAVA_HOME if needed: export JAVA_HOME=/path/to/java")
        print("3. Check PySpark installation: pip install pyspark")
        print("\nIf you're using PySpark 4.0+, try downgrading:")
        print("  pip install 'pyspark<4.0'")
        print("\nOr set these environment variables before running:")
        print("  export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home")
        print("  export PYSPARK_PYTHON=python3")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

