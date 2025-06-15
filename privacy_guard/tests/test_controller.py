import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import should_dim_screen, dim_screen, restore_brightness, get_screen_controller

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the screen controller singleton before each test."""
    import controller
    controller._screen_controller = None
    yield
    controller._screen_controller = None

@pytest.fixture
def mock_screen_controller():
    """Mock the ScreenController class and its instance."""
    with patch('controller.ScreenController') as mock_class:
        # Create a mock instance
        mock_instance = MagicMock()
        mock_instance.dim_screen.return_value = True
        mock_instance.restore_brightness.return_value = True
        # Make the class return our mock instance
        mock_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_face_detection():
    """Mock the face detection functionality."""
    with patch('controller.FaceDetectionAgent') as mock_class:
        mock_instance = MagicMock()
        mock_instance.get_face_count.return_value = 2  # Default to 2 faces
        mock_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_sensitivity_checker():
    """Mock the sensitivity checker."""
    with patch('controller.SensitivityChecker') as mock_class:
        mock_instance = MagicMock()
        mock_instance.is_sensitive.return_value = True  # Default to sensitive content
        mock_class.return_value = mock_instance
        yield mock_instance

def test_should_dim_screen_with_sensitive_content(mock_screen_controller, mock_face_detection, mock_sensitivity_checker):
    """Test that screen dims when multiple faces and sensitive content are detected."""
    # Setup mocks
    mock_face_detection.get_face_count.return_value = 2
    mock_sensitivity_checker.is_sensitive.return_value = True
    
    browser_data = {
        "url": "https://example.com/sensitive",
        "dom": "<html><body>Sensitive content</body></html>"
    }
    
    result = should_dim_screen(browser_data)
    
    assert result is True
    mock_screen_controller.dim_screen.assert_called_once()
    mock_sensitivity_checker.is_sensitive.assert_called_once_with(
        browser_data['dom'],
        browser_data['url']
    )

def test_should_dim_screen_with_non_sensitive_content(mock_screen_controller, mock_face_detection, mock_sensitivity_checker):
    """Test that screen doesn't dim when content is not sensitive."""
    # Setup mocks
    mock_face_detection.get_face_count.return_value = 2
    mock_sensitivity_checker.is_sensitive.return_value = False
    
    browser_data = {
        "url": "https://example.com/public",
        "dom": "<html><body>Public content</body></html>"
    }
    
    result = should_dim_screen(browser_data)
    
    assert result is False
    mock_screen_controller.restore_brightness.assert_called_once()
    mock_sensitivity_checker.is_sensitive.assert_called_once()

def test_should_dim_screen_with_single_face(mock_screen_controller, mock_face_detection, mock_sensitivity_checker):
    """Test that screen doesn't dim when only one face is detected."""
    # Setup mocks
    mock_face_detection.get_face_count.return_value = 1
    mock_sensitivity_checker.is_sensitive.return_value = True
    
    browser_data = {
        "url": "https://example.com/sensitive",
        "dom": "<html><body>Sensitive content</body></html>"
    }
    
    # Reset the singleton to ensure we get a fresh mock
    import controller
    controller._screen_controller = None
    
    result = should_dim_screen(browser_data)
    
    assert result is False
    mock_screen_controller.restore_brightness.assert_called_once()
    # Sensitivity checker should not be called when only one face is detected
    mock_sensitivity_checker.is_sensitive.assert_not_called()

def test_dim_screen_manual(mock_screen_controller):
    """Test manual screen dimming."""
    result = dim_screen(30)
    
    assert result is True
    mock_screen_controller.dim_screen.assert_called_once_with(30)

def test_restore_brightness(mock_screen_controller):
    """Test restoring screen brightness."""
    result = restore_brightness()
    
    assert result is True
    mock_screen_controller.restore_brightness.assert_called_once()

def test_screen_controller_singleton():
    """Test that get_screen_controller returns a singleton instance."""
    controller1 = get_screen_controller()
    controller2 = get_screen_controller()
    
    assert controller1 is controller2 