# Contributing to AI Spark Performance Coach

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/ai-spark-performance-coach.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate it: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
5. Install in development mode: `pip install -e ".[dev,ai]"`

## Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev,ai]"

# Run tests (when implemented)
pytest

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions/classes
- Keep functions focused and small
- Add tests for new features

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests and linting
4. Commit with clear messages
5. Push to your fork
6. Create a Pull Request

## Areas for Contribution

- Additional performance issue detection rules
- Support for more LLM providers (Anthropic, local models, etc.)
- Databricks event log support
- Better visualization/formatting
- More comprehensive tests
- Documentation improvements

