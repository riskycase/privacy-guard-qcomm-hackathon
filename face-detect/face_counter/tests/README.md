# Face Counter Tests

This directory contains unit tests for the face counter module. The tests are designed to run without requiring the actual ONNX model, using mocks instead.

## Setup

1. Install test dependencies:

```bash
cd face_counter/tests
pip install -r requirements-test.txt
```

## Running Tests

To run all tests, make sure you're in the face_counter directory:

```bash
cd ..  # Go to face_counter directory if you're in tests
pytest tests/
```

Or run from the tests directory with the PYTHONPATH set:

```bash
PYTHONPATH=$PYTHONPATH:.. pytest
```

To run tests with coverage report:

```bash
cd ..  # Go to face_counter directory
pytest --cov=. tests/
```

## Test Structure

The tests cover the following functionality:

- Image preprocessing
- Peak finding in heatmaps
- Face detection with mock model outputs
- Face counting
- Edge cases (empty frames, invalid inputs)

## Notes

- The tests use mocking to avoid requiring the actual ONNX model
- All tests are designed to be independent and can run in any order
- Test fixtures are used to provide common test objects
- The tests verify both successful cases and error handling
- Uses the existing virtual environment from the parent face-detect directory
- Tests are run as a proper Python package with proper import paths
