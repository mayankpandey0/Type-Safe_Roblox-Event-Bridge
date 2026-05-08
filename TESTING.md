# Testing Guide

Welcome to the testing guide for the Type-Safe Roblox Event Bridge!

As we build robust infrastructure for Roblox, ensuring our schemas and compilation pipelines are error-free is critical. We use `pytest` for all unit testing.

## Running Tests Locally

1. **Install Requirements**: Ensure you have `pytest` installed.
   ```bash
   pip install pytest
   ```

2. **Execute Tests**: Run `pytest` from the root directory. You can specify the `tests/` folder explicitly.
   ```bash
   PYTHONPATH=. pytest tests/
   ```

## Test Structure

Our tests are organized to mirror the `core` structure:
- `tests/test_ir_models.py` - Validates the structure and initialization of Intermediate Representation models.
- `tests/test_registry.py` - Ensures our type resolution, circular dependency checks, and deterministic identifiers are completely sound.

## Writing New Tests

When adding a new feature (e.g., a new compiler pass in `core/passes`), follow these guidelines:
- **Isolate the unit**: Don't test the entire compiler pipeline if you are just adding a new validation rule. Instantiate the pass and test it directly.
- **Test Edge Cases**: Always add tests for invalid schemas, missing fields, and circular dependencies.
- **Naming Convention**: Prefix your test files with `test_` and your test functions with `test_` so that `pytest` can auto-discover them.

## Continuous Integration (CI)

We run a GitHub Actions workflow on every push and pull request to the `main` branch. You can find the configuration in `.github/workflows/ci.yml`. This ensures that regressions are caught automatically before they reach production.

Happy coding! If you're learning, writing tests is the best way to understand how the codebase works.
