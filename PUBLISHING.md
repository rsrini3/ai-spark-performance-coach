# Publishing Guide

This guide explains how to publish the AI Spark Performance Coach package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (for testing): Create an account at https://test.pypi.org/account/register/
3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf build/ dist/ *.egg-info
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

   This creates:
   - `dist/ai_spark_performance_coach-0.1.0-py3-none-any.whl` (wheel)
   - `dist/ai_spark_performance_coach-0.1.0.tar.gz` (source distribution)

## Testing the Build

1. **Install locally to test**:
   ```bash
   pip install dist/ai_spark_performance_coach-0.1.0-py3-none-any.whl
   ```

2. **Test the installation**:
   ```bash
   ai-spark-coach --help
   ```

## Publishing to TestPyPI (Recommended First Step)

1. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Install from TestPyPI to verify**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ ai-spark-performance-coach
   ```

## Publishing to PyPI

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

2. **Verify on PyPI**: Check https://pypi.org/project/ai-spark-performance-coach/

## Version Bumping

Before publishing a new version:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or appropriate version
   ```

2. Update `CHANGELOG.md` with new changes

3. Commit and tag:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.1"
   git tag v0.1.1
   git push origin main --tags
   ```

## Checklist Before Publishing

- [ ] Version number updated in `pyproject.toml`
- [ ] `CHANGELOG.md` updated
- [ ] All tests pass (when implemented)
- [ ] Code is linted and formatted
- [ ] README is up to date
- [ ] LICENSE file is present
- [ ] `.gitignore` excludes build artifacts
- [ ] Package builds successfully
- [ ] Tested installation locally
- [ ] Tested on TestPyPI (optional but recommended)

## Post-Publishing

After successful publication:

1. Create a GitHub release with the changelog
2. Update documentation if needed
3. Announce on relevant channels (if applicable)

