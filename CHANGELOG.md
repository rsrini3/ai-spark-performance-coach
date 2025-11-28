# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-28

### Added
- Initial release
- Spark event log parsing
- Performance issue detection (skew, large shuffles, long stages)
- Rule-based recommendations
- OpenAI integration for AI-powered recommendations
- Command-line interface
- Support for .env file configuration
- Example scripts for generating Spark event logs

### Features
- Parse Spark event logs (supports .gz files)
- Detect task skew, large shuffles, and long-running stages
- Generate human-readable performance reports
- AI-powered tuning recommendations (optional)
- Rule-based fallback recommendations

