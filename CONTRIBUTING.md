# Contributing to Connection Identity

First off, thank you for considering contributing to Connection Identity! It's people like you that make open source such a great community.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally.
3. Create a new branch for your feature or bugfix (`git checkout -b feature/my-awesome-feature`).

## Local Development

We use Python and Docker for local development.

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Testing your changes
Before submitting a pull request, please ensure that:
1. The code is formatted according to our style guidelines:
   ```bash
   black .
   ```
2. All unit tests pass successfully:
   ```bash
   pytest tests/
   ```

## Pull Request Process

1. Ensure your PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
2. Your PR will automatically trigger our GitHub Actions CI/CD pipeline.
3. The pipeline will run `black` formatting checks and `pytest`. **If these fail, your PR cannot be merged.**
4. Once the checks pass, a maintainer will review your code.

Thank you for contributing!
