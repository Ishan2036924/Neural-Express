# Contributing to Neural Express

First off, thank you for considering contributing to Neural Express! It's people like you that make Neural Express such a great tool for the AI community.

## 🎯 Ways to Contribute

### 1. Report Bugs

If you find a bug, please create an issue on GitHub with:

- **Clear title** - Summarize the problem in one line
- **Description** - Detailed explanation of the issue
- **Steps to reproduce** - Step-by-step instructions
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Environment** - OS, Python version, Neural Express version
- **Logs** - Relevant error messages or logs

**Example:**
```
Title: RSS feed fails with 403 error for OpenAI Blog

Description: When running in daily mode, the OpenAI Blog feed
consistently returns a 403 Forbidden error.

Steps to reproduce:
1. Run `python -m neural_express run --mode daily`
2. Check logs in output/neural_express.log

Expected: Feed fetches successfully
Actual: 403 Forbidden error

Environment:
- OS: macOS 14.0
- Python: 3.10.5
- Neural Express: 2.0.0

Logs:
ERROR | neural_express.ingestion.rss | HTTP error fetching
OpenAI Blog: Client error '403 Forbidden'
```

### 2. Suggest Features

Have an idea for a new feature? Create an issue with:

- **Feature title** - Clear, concise name
- **Problem statement** - What problem does this solve?
- **Proposed solution** - How would it work?
- **Alternatives considered** - Other approaches you thought about
- **Use cases** - Real-world scenarios where this helps

### 3. Improve Documentation

Documentation improvements are always welcome:

- Fix typos or clarify confusing sections
- Add examples or use cases
- Improve code comments
- Translate documentation

### 4. Contribute Code

Ready to write code? Great! Follow the guidelines below.

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/neural_express_project.git
cd neural_express_project

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/neural_express_project.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black ruff

# Copy example environment file
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 3. Create a Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Adding tests

---

## 💻 Development Guidelines

### Code Style

We use **Black** for code formatting and **Ruff** for linting.

**Before committing, run:**

```bash
# Format code with Black
black neural_express/

# Lint with Ruff
ruff check neural_express/

# Fix auto-fixable issues
ruff check --fix neural_express/
```

**Configuration:**
- Line length: 88 (Black default)
- Python version: 3.10+
- Import sorting: Ruff handles this

### Code Standards

1. **Type Hints**
   ```python
   # Good
   def fetch_feed(url: str, timeout: int = 30) -> list[NewsItem]:
       pass

   # Bad
   def fetch_feed(url, timeout=30):
       pass
   ```

2. **Docstrings** (Google style)
   ```python
   def deduplicate(items: list[NewsItem]) -> list[NewsItem]:
       """
       Deduplicate news items by clustering similar content.

       Args:
           items: List of news items to deduplicate

       Returns:
           List of unique news items with duplicates tracked
       """
       pass
   ```

3. **Error Handling**
   ```python
   # Good - Specific exceptions, continue on failure
   try:
       result = fetch_feed(url)
   except httpx.HTTPError as e:
       logger.error(f"Failed to fetch {url}: {e}")
       return []

   # Bad - Bare except, stops pipeline
   try:
       result = fetch_feed(url)
   except:
       raise
   ```

4. **Logging**
   ```python
   from ..utils.logging import get_logger
   logger = get_logger(__name__)

   logger.info("Starting process")
   logger.debug(f"Processing {len(items)} items")
   logger.warning("Feed returned no items")
   logger.error(f"Failed: {error}")
   ```

### Testing

**Write tests for new features:**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=neural_express --cov-report=html

# Run specific test file
pytest tests/test_dedupe.py -v

# Run specific test
pytest tests/test_dedupe.py::test_deduplicator_creation -v
```

**Test structure:**
```python
# tests/test_module.py
import pytest
from neural_express.module import function

def test_function_success():
    """Test function with valid input."""
    result = function(valid_input)
    assert result == expected_output

def test_function_edge_case():
    """Test function with edge case."""
    result = function(edge_case_input)
    assert result is not None

def test_function_error_handling():
    """Test function handles errors gracefully."""
    with pytest.raises(ValueError):
        function(invalid_input)
```

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Refactoring (no feat/fix)
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(dedupe): add story chain detection for weekly mode

Implements smart deduplication that detects related stories
across multiple days by analyzing similarity scores and
publication dates.

Closes #42

---

fix(rss): handle 403 errors gracefully

RSS feeds that return 403 now log warning and continue
pipeline instead of stopping execution.

Fixes #38

---

docs(readme): add story chain detection section

Added documentation explaining how story chains work in
weekly mode with examples.
```

---

## 📝 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines (Black + Ruff)
- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] New tests added for new features
- [ ] Documentation updated (README, ARCHITECTURE, docstrings)
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

```bash
# Update your branch
git fetch upstream
git rebase upstream/main
```

### 2. Create Pull Request

**Title format:**
```
<type>: <short description>

Examples:
feat: Add PDF export functionality
fix: Resolve RSS feed timeout issues
docs: Update installation instructions
```

**Description template:**
```markdown
## Description
Brief summary of changes and motivation.

## Changes
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Tested locally with `pytest`
- [ ] Tested with real RSS feeds
- [ ] Verified output (MD + PDF)

## Screenshots (if applicable)
[Add screenshots of UI changes, PDF output, etc.]

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
Related to #456
```

### 3. Review Process

1. **Automated Checks** - CI runs tests and linting
2. **Code Review** - Maintainer reviews code
3. **Feedback** - Address any requested changes
4. **Approval** - Once approved, PR will be merged
5. **Merge** - Squash and merge or rebase (maintainer decides)

### 4. After Merge

```bash
# Update your fork
git checkout main
git pull upstream main
git push origin main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🐛 Bug Fix Process

### 1. Reproduce the Bug

```bash
# Create test that demonstrates the bug
# tests/test_bugfix.py

def test_bug_reproduction():
    """Test demonstrating bug #123."""
    # This test should FAIL before your fix
    result = buggy_function()
    assert result == expected
```

### 2. Fix the Bug

```python
# Make minimal changes to fix the issue
# Add logging to help future debugging
logger.debug("Processing edge case")
```

### 3. Verify Fix

```bash
# Test should now PASS
pytest tests/test_bugfix.py -v

# Run full test suite
pytest tests/ -v

# Test manually if needed
python -m neural_express run --mode daily --verbose
```

### 4. Document the Fix

```python
# Add comment explaining the fix
# Fix for issue #123: Handle empty feed response
if not entries:
    logger.warning(f"Feed {url} returned no entries")
    return []
```

---

## 🎨 Feature Development Process

### 1. Discuss First

For major features, **create an issue first** to discuss:
- Is this feature aligned with project goals?
- What's the best approach?
- Are there breaking changes?

### 2. Design

- Update `ARCHITECTURE.md` if adding new modules
- Consider backward compatibility
- Think about configuration options
- Plan error handling

### 3. Implement

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Implement in small, logical commits
git add neural_express/new_module.py
git commit -m "feat(module): add new module skeleton"

git add tests/test_new_module.py
git commit -m "test(module): add tests for new module"

git add README.md
git commit -m "docs: document new module in README"
```

### 4. Test Thoroughly

- Unit tests for all new functions
- Integration test for full feature
- Test with real data (not just mocks)
- Test error cases

### 5. Document

- Update README.md
- Update ARCHITECTURE.md if architectural changes
- Add docstrings to all new functions
- Add usage examples

---

## 📦 Adding New Dependencies

### Guidelines

1. **Justify the dependency**
   - Is it really needed?
   - Can we use stdlib instead?
   - Is it well-maintained?

2. **Update requirements.txt**
   ```bash
   # Add to requirements.txt with version
   new-package>=1.0.0

   # Update lock file (if using pip-tools)
   pip-compile requirements.txt
   ```

3. **Document why it's needed**
   ```python
   # requirements.txt
   # New dependency for feature X
   new-package>=1.0.0  # Provides Y functionality
   ```

---

## 🔍 Code Review Checklist

**For Reviewers:**

- [ ] Code is clear and maintainable
- [ ] Tests cover new functionality
- [ ] No obvious bugs or security issues
- [ ] Performance considerations addressed
- [ ] Documentation is updated
- [ ] Backward compatibility maintained
- [ ] Error handling is robust
- [ ] Logging is appropriate

**For Contributors:**

- [ ] Self-reviewed code
- [ ] Removed debug statements
- [ ] No commented-out code
- [ ] No hardcoded values (use config)
- [ ] Secrets not in code (use .env)

---

## ❓ Questions?

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Open an Issue
- **Security Issues**: Email security@neuralexpress.ai (private)
- **Feature Requests**: Open an Issue with [Feature] tag

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct reasonably considered inappropriate

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report issues to: conduct@neuralexpress.ai

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages

Thank you for contributing to Neural Express! 🚀

---

**Questions about contributing?** Open an issue with the `question` label.
