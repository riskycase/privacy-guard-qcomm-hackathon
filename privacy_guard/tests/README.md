# Privacy Guard Test Suite

This directory contains the test suite for the Privacy Guard module. The tests ensure the reliability and correctness of the screen dimming functionality based on face detection and content sensitivity.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test configuration
├── test_controller.py       # Tests for the main controller logic
├── test_screen_control.py   # Tests for screen brightness control
└── requirements-test.txt    # Test dependencies
```

## Test Coverage

### Controller Tests (`test_controller.py`)

Tests the main controller logic that determines when to dim the screen:

- `test_should_dim_screen_with_sensitive_content`: Verifies screen dims when multiple faces and sensitive content are detected
- `test_should_dim_screen_with_non_sensitive_content`: Verifies screen doesn't dim when content is not sensitive
- `test_should_dim_screen_with_single_face`: Verifies screen doesn't dim when only one face is detected
- `test_dim_screen_manual`: Tests manual screen dimming functionality
- `test_restore_brightness`: Tests screen brightness restoration
- `test_screen_controller_singleton`: Verifies singleton pattern for screen controller

### Screen Control Tests (`test_screen_control.py`)

Tests the screen brightness control functionality:

- `test_get_current_brightness_success`: Verifies successful retrieval of current brightness
- `test_get_current_brightness_failure`: Tests handling of brightness retrieval failure
- `test_dim_screen_success`: Verifies successful screen dimming
- `test_dim_screen_failure`: Tests handling of dimming failure
- `test_restore_brightness_success`: Verifies successful brightness restoration
- `test_restore_brightness_failure`: Tests handling of restoration failure
- `test_dim_screen_with_default_percentage`: Verifies default dimming behavior

## Running Tests

1. Install test dependencies:

```bash
pip install -r requirements-test.txt
```

2. Run all tests:

```bash
pytest
```

3. Run tests with coverage:

```bash
pytest --cov=privacy_guard tests/
```

4. Run specific test file:

```bash
pytest tests/test_controller.py
pytest tests/test_screen_control.py
```

5. Run with verbose output:

```bash
pytest -v
```

## Test Dependencies

The test suite requires the following packages (specified in `requirements-test.txt`):

- pytest==7.4.3
- pytest-cov==4.1.0
- pytest-mock==3.12.0
- requests-mock==1.11.0
- python-dotenv==1.0.0

## Mocking Strategy

The tests use Python's `unittest.mock` to mock external dependencies:

1. **Controller Tests**:

   - Mocks `ScreenController` for screen control operations
   - Mocks `FaceDetectionAgent` for face detection
   - Mocks `SensitivityChecker` for content sensitivity checks

2. **Screen Control Tests**:
   - Mocks `subprocess.run` for PowerShell commands
   - Simulates both successful and failed operations
   - Verifies exact PowerShell commands

## Environment Setup

The `conftest.py` file sets up the test environment with:

- Mock API endpoints
- Test environment variables
- Shared fixtures for common test setup

## Best Practices

1. **Test Isolation**: Each test is independent and doesn't rely on state from other tests
2. **Mocking**: External dependencies are properly mocked
3. **Error Handling**: Both success and failure cases are tested
4. **Command Verification**: Exact PowerShell commands are verified
5. **Singleton Handling**: Screen controller singleton is properly reset between tests

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<functionality>_<scenario>`
2. Use appropriate fixtures from `conftest.py`
3. Mock all external dependencies
4. Include both success and failure cases
5. Add docstrings explaining the test purpose
6. Update this README if adding new test categories

## Troubleshooting

Common issues and solutions:

1. **Import Errors**:

   - Ensure you're running tests from the correct directory
   - Check that `__init__.py` exists in all necessary directories

2. **Mock Issues**:

   - Verify mock paths are correct
   - Reset mocks between tests if needed
   - Check mock assertions match actual calls

3. **PowerShell Command Failures**:

   - Verify exact command strings in assertions
   - Check mock setup for subprocess calls

4. **Singleton Issues**:
   - Reset the screen controller singleton between tests
   - Use fresh mock instances for each test
