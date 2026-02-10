# Developer Documentation

This document contains technical information for developers working on the Falcon FDR Dictionary project.

## Project Structure

```
falcon-fdr-dictionary/
├── falcon_fdr_dictionary/          # Main Python package
│   ├── __init__.py                 # Package initialization
│   ├── api_client.py               # FDR API client (SOLID: Single Responsibility)
│   ├── cli.py                      # Click-based CLI (Command pattern)
│   ├── config.py                   # Configuration management
│   └── tagging.py                  # Event tagging logic
├── bin/                            # Entry point shims
│   └── falcon-fdr-events-dictionary  # Shim script (no business logic)
├── tests/                          # Test suite
│   └── test_tagdictionary.py       # Tagging tests
├── docs/                           # Generated output directory
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore patterns
├── pyproject.toml                  # Modern Python project configuration
├── LICENSE                         # License file
├── README.md                       # User documentation
└── DEV.md                          # This file

```

## Architecture

### Design Principles (SOLID)

The codebase follows SOLID principles:

**Single Responsibility Principle (SRP)**
- `api_client.py`: Handles only FDR API communication
- `tagging.py`: Handles only event tagging logic
- `config.py`: Handles only configuration management
- `cli.py`: Handles only CLI interface

**Open/Closed Principle (OCP)**
- Tagging keywords can be extended without modifying core logic
- New CLI commands can be added via Click decorators

**Liskov Substitution Principle (LSP)**
- Config can be created from environment or CLI overrides interchangeably

**Interface Segregation Principle (ISP)**
- Each module exposes only necessary public methods
- FDRClient provides focused API methods

**Dependency Inversion Principle (DIP)**
- CLI depends on abstractions (Config, FDRClient) not implementations
- Configuration is injected, not hardcoded

### DRY Principle

Code reuse through:
- Shared config management (`get_config()`)
- Reusable API client (`FDRClient`)
- Common tagging logic (`tag_event()`, `tag_dictionary()`)
- No duplication between CLI and shim

### Command/Subcommand Pattern

The CLI uses Click's command pattern:
```python
@click.group()
def cli():
    """Main command group"""

@cli.command()
def generate():
    """Subcommand"""

@cli.command()
def tag():
    """Subcommand"""
```

This provides:
- Clean separation of concerns
- Easy command discovery
- Automatic help generation
- Extensibility for new commands

## Module Details

### api_client.py

**FDRClient Class**

Responsible for all CrowdStrike API interactions:
- Authentication via FalconPy
- Paginated dictionary retrieval
- Individual event schema fetching
- Credential validation

Key methods:
- `authenticate()`: Authenticate with CrowdStrike
- `get_dictionary_page()`: Fetch paginated results
- `get_dictionary_item()`: Fetch specific event
- `validate_credentials()`: Test credentials and API access

### config.py

**Config Dataclass**

Manages application configuration:
- Uses `python-dotenv` to load `.env` file
- Supports environment variable overrides
- Provides CLI override capability
- Validates configuration (e.g., cloud region)

Pattern:
```python
config = Config.from_env()  # Load from environment
config = get_config(client_id="...", client_secret="...")  # With overrides
```

### tagging.py

**Event Tagging Logic**

Adds metadata to FDR events:
- Expands CamelCase names to human-readable format
- Extracts contextual tags via keyword matching
- Tracks untagged events

Key functions:
- `extract_tags()`: Find matching tags in text
- `expand_name()`: Convert CamelCase to spaces
- `tag_event()`: Tag single event
- `tag_dictionary()`: Tag all events, return tagged and untagged

### cli.py

**Click-based CLI**

Implements three subcommands:

**generate**: Fetch FDR dictionary
- Authenticates with API
- Shows progress bar during fetch
- Saves to JSON file
- Handles pagination automatically

**tag**: Add tags and expanded names
- Reads JSON dictionary
- Applies tagging logic
- Reports untagged events
- Saves to new JSON file

**validate**: Test credentials
- Verifies authentication
- Tests FDR API access
- Reports API details
- Exits with appropriate status code

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or poetry
- Git

### Clone and Install

```bash
# Clone repository
git clone https://github.com/cs-shadowbq/falcon-fdr-dictionary
cd falcon-fdr-dictionary

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=falcon_fdr_dictionary --cov-report=html

# Run specific test file
pytest tests/test_tagdictionary.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black falcon_fdr_dictionary/

# Check with flake8
flake8 falcon_fdr_dictionary/

# Lint with pylint
pylint falcon_fdr_dictionary/
```

### Manual Testing

```bash
# Test the shim
./bin/falcon-fdr-events-dictionary --help

# Test as module
python -m falcon_fdr_dictionary.cli --help

# Test after installation
falcon-fdr-events-dictionary --help
```

## Adding New Features

### Adding a New CLI Command

1. Add command to `cli.py`:

```python
@cli.command()
@click.option('--option', help='Description')
def newcommand(option: str):
    """New command description."""
    # Implementation
```

2. Update README.md with usage examples
3. Add tests if needed
4. Update DEV.md if architecture changes

### Adding New Tag Keywords

Edit `KEYWORDS` dictionary in `tagging.py`:

```python
KEYWORDS = {
    'existing_tag': ['keyword1', 'keyword2'],
    'new_tag': ['new_keyword1', 'new_keyword2'],  # Add here
}
```

### Adding Configuration Options

1. Add field to `Config` dataclass in `config.py`:

```python
@dataclass
class Config:
    new_option: str = "default_value"
```

2. Update `from_env()` to read from environment:

```python
new_option=os.getenv("NEW_OPTION", "default_value")
```

3. Update `.env.example` with documentation
4. Update README.md configuration section

## Build and Release

### Building Distribution

```bash
# Build wheel and source distribution
python -m build

# Check distribution
twine check dist/*
```

### Publishing to PyPI

```bash
# Test with TestPyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Version Bumping

Update version in:
1. `pyproject.toml` - `[project] version`
2. `falcon_fdr_dictionary/__init__.py` - `__version__`
3. `falcon_fdr_dictionary/cli.py` - `VERSION`

## Dependencies

### Runtime Dependencies

- `crowdstrike-falconpy>=1.5.4` - CrowdStrike API SDK
- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Rich terminal output
- `tabulate>=0.9.0` - Table formatting
- `python-dotenv>=1.0.0` - Environment file handling

### Development Dependencies

- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `flake8>=6.0.0` - Linting
- `pylint>=3.0.0` - Advanced linting
- `black>=23.0.0` - Code formatting

## Troubleshooting Development Issues

### Import Errors During Development

If you get import errors:
```bash
pip install -e .
```

### Tests Failing

Make sure you have dev dependencies:
```bash
pip install -e ".[dev]"
```

### Shim Not Working

Check executable permissions:
```bash
chmod +x bin/falcon-fdr-events-dictionary
```

### Module Not Found After Install

Reinstall in development mode:
```bash
pip uninstall falcon-fdr-dictionary
pip install -e .
```

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes
- Use f-strings for string formatting

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """Short one-line description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception occurs
    """
```

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

Example: `feat: add validate subcommand for credential testing`

## Testing Strategy

### Unit Tests

Test individual functions:
- Tag extraction logic
- Name expansion
- Configuration loading

### Integration Tests

Test component interaction:
- API client with mocked responses
- CLI commands end-to-end
- Configuration with environment variables

### Manual Testing Checklist

Before release:
- [ ] All CLI commands work
- [ ] Help text displays correctly
- [ ] Error messages are clear
- [ ] Progress indicators work
- [ ] Output files are valid JSON
- [ ] Shim script works
- [ ] Module import works
- [ ] Tests pass

## Project Decisions

### Why Click?

- Industry standard for Python CLIs
- Excellent documentation
- Built-in help generation
- Easy to test
- Supports complex command hierarchies

### Why Rich?

- Beautiful terminal output
- Built-in progress bars
- Excellent table rendering
- Better than jtbl for modern CLIs
- Active development

### Why python-dotenv?

- Industry standard for environment management
- Simple and reliable
- Matches cao-report-fetcher pattern
- Better than hardcoded paths

### Why dataclasses?

- Type safety
- Less boilerplate than classes
- Built into Python 3.8+
- Easy to test and validate

### Why No requirements.txt?

- `pyproject.toml` is the modern standard
- Single source of truth
- Better dependency resolution
- Required for PEP 517/518 compliance

## Maintenance

### Regular Tasks

- Update dependencies quarterly
- Review and merge dependabot PRs
- Update FalconPy when new versions release
- Re-validate against CrowdStrike API changes

### Monitoring

Watch for:
- CrowdStrike API changes
- FalconPy breaking changes
- Python version deprecations
- Security advisories

## Support

For questions or issues:
1. Check README.md for user documentation
2. Check this file for development details
3. Review existing GitHub issues
4. Open new issue with detailed description

## License

See LICENSE file for project license details.
