# AI Spark Performance Coach

An **AI-assisted Spark performance analysis tool** that reads **Spark event logs**, extracts key metrics about stages/tasks/shuffle, detects potential performance issues (skew, heavy shuffles, etc.), and then uses a **language model** to explain the problems and suggest tuning ideas in plain English.

This is designed so you can run it locally with a single-node Spark and later extend it to Databricks event logs.

---

## Features (v0.1)

- Parses **Spark event logs** (`spark.eventLog.enabled=true`) from local Spark.
- Summarizes:
  - Stages
  - Number of tasks
  - Median vs max task duration
  - Shuffle read size
- Detects:
  - **Skewed stages** (max task duration ≫ median)
  - **Shuffle-heavy stages** (large shuffle read)
  - **Long-running stages** (taking significant portion of total time)
- Builds a **compact prompt** for a GenAI model.
- Prints an **"AI performance review"** with tuning suggestions.

> Note: The `ai_coach.py` file includes a placeholder for the LLM call.
> You can wire it to OpenAI, a local model, or any provider you prefer.

---

## Quickstart

### 1. Install

**Basic installation (rule-based recommendations only):**
```bash
cd ai-spark-performance-coach
pip install -e .
```

**With AI/LLM support (recommended):**
```bash
pip install -e ".[ai]"
# Or install all optional dependencies:
pip install -e ".[all]"
```

**Using requirements.txt:**
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# For AI support, also install:
pip install openai python-dotenv
```

### 2. Generate a Spark Event Log

First, install PySpark (if not already installed):
```bash
pip install pyspark
```

Then, run the example script to generate an event log:

```bash
python examples/generate_spark_log.py
```

Or manually run a Spark job with event logging enabled:

```python
import os
# Set JAVA_HOME before importing PySpark (important!)
os.environ["JAVA_HOME"] = "/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
    SparkSession.builder
    .appName("test-job")
    .config("spark.eventLog.enabled", "true")
    .config("spark.eventLog.dir", "file:///tmp/spark-events")
    .getOrCreate()
)

# Your Spark code here
df = spark.range(0, 10_000_000).withColumn("k", col("id") % 1000)
df2 = df.groupBy("k").count()
df2.collect()

spark.stop()
```

This will create event logs in `/tmp/spark-events/`.

### 3. Analyze the Event Log

```bash
# Basic usage
python -m ai_spark_coach.cli --event-log /tmp/spark-events/app-20251128-0001

# Or if installed as package
ai-spark-coach --event-log /tmp/spark-events/app-20251128-0001

# Save report to file
ai-spark-coach --event-log /tmp/spark-events/app-20251128-0001 --output report.txt

# Use rule-based recommendations only (no LLM)
ai-spark-coach --event-log /tmp/spark-events/app-20251128-0001 --no-llm
```

### 4. Example Output

```
======================================================================
SPARK PERFORMANCE ANALYSIS
======================================================================

Total Jobs: 1
Total Stages: 2
Total Duration: 45.3s

STAGE BREAKDOWN:
----------------------------------------------------------------------
Stage 0: Stage 0
  Duration: 5.2s (11% of total)
  Tasks: 200
  Shuffle Read: 0.0 MB

Stage 1: Stage 1
  Duration: 40.1s (89% of total)
  Tasks: 200
  Shuffle Read: 2300.5 MB

======================================================================
DETECTED ISSUES
======================================================================

HIGH SEVERITY:
  ⚠️  Stage 1 took 89% of total time (40.1s)
  ⚠️  Very large shuffle detected: 2300.5 MB read
  ⚠️  Task skew detected: max task took 80.0s while median task took 5.0s (ratio: 16.0x)

======================================================================
RECOMMENDATIONS
======================================================================

Stage 1 - Large Shuffle (2300.5 MB):
  • Consider using broadcast join if one table is small (< 2GB)
  • Repartition before the join to reduce shuffle size
  • Check if join keys are properly distributed
  • Consider using bucketing for frequently joined tables

Stage 1 - Task Skew:
  • Consider repartitioning on a different key
  • Use salting technique to distribute skewed keys
  • Check for data skew in join keys or groupBy columns
```

---

## Project Structure

```
ai-spark-performance-coach/
├── README.md
├── pyproject.toml
├── requirements.txt
├── src/
│   └── ai_spark_coach/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── spark_log_parser.py # Parse Spark event logs
│       ├── rules.py            # Performance issue detection rules
│       └── ai_coach.py         # Generate AI-powered recommendations
└── examples/
    └── sample_usage.md
```

---

## Using AI-Powered Recommendations

The tool includes built-in OpenAI integration! To use AI-powered recommendations:

### 1. Install AI Dependencies

```bash
# Install with AI support
pip install -e ".[ai]"

# Or install dependencies separately
pip install openai python-dotenv
```

### 2. Set Up Your OpenAI API Key

**Option A: Using .env file (Recommended)**

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
```

The tool will automatically load this file.

**Option B: Environment Variable**

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

**Option C: Command Line**

```bash
ai-spark-coach --event-log /path/to/log --api-key your-key-here
```

### 3. Use AI Recommendations

By default, the tool will use AI recommendations if an API key is found:

```bash
ai-spark-coach --event-log /tmp/spark-events/app-20251128-0001
```

To use a specific model:

```bash
ai-spark-coach --event-log /path/to/log --model gpt-4o-mini
```

To disable AI and use rule-based recommendations only:

```bash
ai-spark-coach --event-log /path/to/log --no-llm
```

### Default Behavior

- If `OPENAI_API_KEY` is found (in .env, environment, or CLI), AI recommendations are used
- If no API key is found, the tool falls back to rule-based recommendations automatically
- You can always force rule-based mode with `--no-llm`

---

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests (when implemented)
pytest

# Format code
black src/

# Lint
ruff check src/
```

---

---

## Troubleshooting

### PySpark Java Errors

If you encounter `TypeError: 'JavaPackage' object is not callable` or similar Java-related errors:

**This is a known issue with PySpark 4.0+**. The recommended solution is to downgrade:

```bash
pip install "pyspark<4.0"
```

Then try running the script again.

**Alternative solutions:**

1. **Set JAVA_HOME before importing PySpark:**
   ```bash
   export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home
   # Or find your Java installation:
   /usr/libexec/java_home
   ```

2. **Verify Java is installed:**
   ```bash
   java -version
   ```

3. **Use the simplified script:**
   ```bash
   python examples/generate_spark_log_simple.py
   ```

4. **Set environment variables:**
   ```bash
   export JAVA_HOME=$(/usr/libexec/java_home)
   export PYSPARK_PYTHON=python3
   export PYSPARK_DRIVER_PYTHON=python3
   ```

### Event Log Not Found

- Make sure `spark.eventLog.enabled=true` is set in your Spark configuration
- Check that the event log directory exists and is writable
- Event logs are typically named with the application ID (e.g., `app-20251128-0001`)

---

## License

MIT

