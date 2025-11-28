#!/usr/bin/env python3
"""
Simplified Spark event log generator that works around PySpark 4.0+ issues.

If you're getting 'JavaPackage' object is not callable errors with PySpark 4.0+,
try downgrading: pip install 'pyspark<4.0'
"""

import os
import sys
from pathlib import Path

# Set environment variables BEFORE any PySpark imports
java_home = os.environ.get("JAVA_HOME")
if not java_home:
    # Auto-detect Java on macOS
    import subprocess
    try:
        java_home = subprocess.check_output(
            ["/usr/libexec/java_home"], text=True
        ).strip()
        os.environ["JAVA_HOME"] = java_home
    except:
        # Fallback to common location
        java_home = "/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home"
        if Path(java_home).exists():
            os.environ["JAVA_HOME"] = java_home

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

print(f"JAVA_HOME: {os.environ.get('JAVA_HOME')}")
print(f"Python: {sys.executable}")

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
except ImportError:
    print("Error: PySpark not installed. Run: pip install pyspark")
    sys.exit(1)

# Check PySpark version
import pyspark
pyspark_version = pyspark.__version__
print(f"PySpark version: {pyspark_version}")

if pyspark_version.startswith("4."):
    print("\n⚠️  WARNING: PySpark 4.0+ has known Java initialization issues.")
    print("   If you encounter errors, downgrade with: pip install 'pyspark<4.0'")
    print()

def main():
    event_log_dir = Path("/tmp/spark-events")
    event_log_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Event log directory: {event_log_dir}")
    
    try:
        # Create SparkSession with minimal config
        spark = (
            SparkSession.builder
            .appName("perf-test")
            .config("spark.eventLog.enabled", "true")
            .config("spark.eventLog.dir", f"file://{event_log_dir}")
            .config("spark.master", "local[2]")  # Use 2 cores to avoid resource issues
            .getOrCreate()
        )
        
        print("✓ Spark session created successfully")
        print("Running test job...")
        
        # Simple job
        df = spark.range(0, 1_000_000).withColumn("k", col("id") % 100)
        result = df.groupBy("k").count().collect()
        
        app_id = spark.sparkContext.applicationId
        event_log_path = event_log_dir / app_id
        
        print(f"\n✓ Job completed!")
        print(f"✓ Event log: {event_log_path}")
        print(f"\nAnalyze with:")
        print(f"  python -m ai_spark_coach.cli --event-log {event_log_path}")
        
        spark.stop()
        
    except TypeError as e:
        if "'JavaPackage' object is not callable" in str(e):
            print("\n❌ PySpark 4.0+ Java initialization error detected.")
            print("\nSOLUTION: Downgrade PySpark to 3.5.x")
            print("  pip install 'pyspark<4.0'")
            print("\nThen run this script again.")
            sys.exit(1)
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

