# Sample Usage Examples

## Example 1: Basic Analysis

```bash
# Generate a Spark event log first
python genLog.py

# Analyze the log
python -m ai_spark_coach.cli --event-log /tmp/spark-events/app-20251128-0001
```

## Example 2: Analyzing a Gzipped Event Log

Spark often compresses event logs. The tool supports both compressed and uncompressed logs:

```bash
ai-spark-coach --event-log /tmp/spark-events/app-20251128-0001.gz
```

## Example 3: Save Report to File

```bash
ai-spark-coach \
  --event-log /tmp/spark-events/app-20251128-0001 \
  --output performance_report.txt
```

## Example 4: Rule-Based Analysis Only

If you don't want to use LLM recommendations (or don't have an API key):

```bash
ai-spark-coach \
  --event-log /tmp/spark-events/app-20251128-0001 \
  --no-llm
```

## Example 5: Using with Databricks Event Logs

When working with Databricks, download the event log and analyze locally:

```bash
# Download from Databricks (example)
# databricks workspace export /path/to/event-log.json /local/path/

ai-spark-coach --event-log /local/path/event-log.json
```

## Example 6: Integration in CI/CD

You can integrate this into your CI/CD pipeline to automatically analyze Spark job performance:

```bash
#!/bin/bash
# ci_analyze_spark.sh

EVENT_LOG=$1
OUTPUT_FILE="spark_performance_report.txt"

ai-spark-coach --event-log "$EVENT_LOG" --output "$OUTPUT_FILE" --no-llm

# Check if high severity issues were found
if grep -q "HIGH SEVERITY" "$OUTPUT_FILE"; then
    echo "⚠️  High severity performance issues detected!"
    cat "$OUTPUT_FILE"
    exit 1
fi
```

## Example 7: Python API Usage

You can also use the library programmatically:

```python
from ai_spark_coach import SparkLogParser, PerformanceRules, AICoach

# Parse event log
parser = SparkLogParser("/tmp/spark-events/app-20251128-0001")
summary = parser.parse()

# Detect issues
issues = PerformanceRules.analyze(summary)

# Generate report
coach = AICoach(use_llm=False)
report = coach.generate_report(summary, issues)
print(report)
```

## Example 8: Custom Spark Job with Event Logging

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, broadcast

# Enable event logging
spark = (
    SparkSession.builder
    .appName("my-spark-job")
    .config("spark.eventLog.enabled", "true")
    .config("spark.eventLog.dir", "file:///tmp/spark-events")
    .config("spark.sql.adaptive.enabled", "true")
    .getOrCreate()
)

# Your Spark operations
df1 = spark.range(0, 100_000_000).withColumn("key", col("id") % 10000)
df2 = spark.range(0, 1000).withColumn("key", col("id"))

# Join operation (this will create shuffle)
result = df1.join(df2, on="key", how="inner")
result.count()

# Get the event log path
app_id = spark.sparkContext.applicationId
event_log_path = f"/tmp/spark-events/{app_id}"

spark.stop()

# Now analyze
import subprocess
subprocess.run([
    "ai-spark-coach",
    "--event-log", event_log_path,
    "--output", "my_job_report.txt"
])
```

