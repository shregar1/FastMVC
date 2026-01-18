# Publishing FastMVC to PyPI

This guide covers publishing FastMVC to the Python Package Index (PyPI).

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens:
   - PyPI: Account Settings → API tokens → Add API token
   - TestPyPI: Same process on test.pypi.org

3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Configuration

### Option 1: Using .pypirc (Traditional)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Secure the file:
```bash
chmod 600 ~/.pypirc
```

### Option 2: Using Environment Variables (Recommended for CI)

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
```

### Option 3: Using keyring (Most Secure)

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your token when prompted
```

## Build Process

### 1. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

### 2. Run Tests

```bash
pytest tests/ -v --cov
```

### 3. Check Code Quality

```bash
black --check .
isort --check .
ruff check .
mypy .
```

### 4. Update Version

Update version in `pyproject.toml` and `fastmvc_cli/__init__.py`:

```toml
# pyproject.toml
[project]
version = "1.0.1"  # Increment appropriately
```

```python
# fastmvc_cli/__init__.py
__version__ = "1.0.1"
```

### 5. Update CHANGELOG

Add release notes to `CHANGELOG.md`.

### 6. Build Package

```bash
python -m build
```

This creates:
- `dist/fastmvc-1.0.0.tar.gz` (source distribution)
- `dist/fastmvc-1.0.0-py3-none-any.whl` (wheel)

### 7. Verify Build

```bash
twine check dist/*
```

## Publishing

### Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ fastmvc
```

### Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify installation
pip install fast-mvc
fastmvc version
```

## GitHub Actions (CI/CD)

Add `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add `PYPI_API_TOKEN` to repository secrets.

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

### Pre-release Versions

```
1.0.0a1   # Alpha
1.0.0b1   # Beta
1.0.0rc1  # Release Candidate
1.0.0     # Final Release
```

## Post-Release

1. **Create Git Tag**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create GitHub Release**:
   - Go to Releases → Draft a new release
   - Select the tag
   - Add release notes from CHANGELOG
   - Attach wheel and tarball from dist/

3. **Announce**:
   - Update documentation
   - Post on social media
   - Update any external references

## Troubleshooting

### "Package already exists"

You cannot overwrite existing versions. Increment the version number.

### "Invalid classifier"

Check classifiers against the [official list](https://pypi.org/classifiers/).

### "README rendering issues"

```bash
# Check README rendering
pip install readme-renderer
python -m readme_renderer README.md
```

### "Missing files in distribution"

Check `MANIFEST.in` and `pyproject.toml` package-data settings.

## Quick Reference

```bash
# Full release process
rm -rf build/ dist/ *.egg-info/
pytest tests/ -v
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Production
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

