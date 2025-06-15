import pytest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ['FACE_API_URL'] = 'http://localhost:5000/api/faces'
    os.environ['LLM_URL'] = 'http://localhost:3001/api/v1/openai/chat/completions'
    os.environ['WORKSPACE_NAME'] = 'test-model'
    os.environ['API_TOKEN'] = 'test-token'
    yield
    # Cleanup if needed 