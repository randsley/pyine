# Contributing to pyine

Thank you for your interest in contributing to pyine! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Python version** and operating system
- **pyine version** you're using
- **Code samples** or error messages if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear title and description** of the enhancement
- **Use cases** - why would this be useful?
- **Possible implementation** - if you have ideas

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run the test suite** to ensure everything passes
6. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Getting Started

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pyine.git
   cd pyine
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest
   ```

## Coding Standards

### Style Guide

- **PEP 8**: Follow Python's PEP 8 style guide
- **Black**: Use Black for code formatting (120 char line length)
- **Ruff**: Use Ruff for linting
- **Type hints**: Add type hints to all function signatures
- **Docstrings**: Use Google-style docstrings for all public APIs

### Code Formatting

Format your code before committing:

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/
```

### Type Checking

Run type checking with mypy:

```bash
mypy src/ --ignore-missing-imports
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/pyine --cov-report=html

# Run specific test file
pytest tests/test_client/test_base.py

# Run tests matching a pattern
pytest -k "test_search"
```

### Writing Tests

- **Unit tests** for individual functions/classes
- **Integration tests** for end-to-end workflows
- **Use fixtures** from `conftest.py` for common test data
- **Mock API calls** using the `responses` library
- **Aim for 80%+ coverage** for new code

Example test structure:

```python
import pytest
import responses

def test_my_feature():
    """Test description."""
    # Arrange
    ...

    # Act
    ...

    # Assert
    ...
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong

    Example:
        >>> my_function("test", 42)
        True
    """
    ...
```

### Updating Documentation

When adding features:

- Update **README.md** with usage examples
- Add entries to **CHANGELOG.md**
- Update **API reference** if needed
- Add **examples/** files for complex features

## Commit Messages

Write clear commit messages:

- **Use present tense**: "Add feature" not "Added feature"
- **Be descriptive**: Explain what and why, not just how
- **Reference issues**: Use `#123` to reference issues

Good commit messages:
```
Add support for custom cache TTL

- Allow users to specify cache_ttl parameter
- Update documentation with new parameter
- Add tests for custom TTL behavior

Fixes #42
```

## Pull Request Process

1. **Update CHANGELOG.md** with your changes
2. **Ensure all tests pass** and coverage remains above 80%
3. **Update documentation** as needed
4. **Request review** from maintainers
5. **Address review comments** promptly
6. **Squash commits** if requested

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted (black)
- [ ] Code is linted (ruff)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

## Questions?

If you have questions:

- **Check existing issues** and discussions
- **Open an issue** for discussion
- **Reach out** to maintainers

## License

By contributing to pyine, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to pyine! 🎉
