import pytest
from unittest.mock import patch, Mock, MagicMock, call
import sys
import os
import subprocess

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screen_control import ScreenController

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for all tests."""
    with patch('subprocess.run') as mock_run:
        # Create a mock process result
        mock_process = MagicMock()
        mock_process.stdout = "75\n"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        yield mock_run

def test_get_current_brightness_success(mock_subprocess):
    """Test successful retrieval of current brightness."""
    # First call is from initialization, second is from our test
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    brightness = controller._get_current_brightness()
    
    assert brightness == 75
    mock_subprocess.assert_called_once_with(
        ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
        capture_output=True,
        text=True,
        check=True
    )

def test_get_current_brightness_failure(mock_subprocess):
    """Test handling of failure to get current brightness."""
    # First call is from initialization
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    # Mock subprocess failure for the test call
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, "powershell")
    
    brightness = controller._get_current_brightness()
    
    assert brightness == 100  # Default value on failure
    mock_subprocess.assert_called_once()

def test_dim_screen_success(mock_subprocess):
    """Test successful screen dimming."""
    # First call is from initialization
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    result = controller.dim_screen(40)
    
    assert result is True
    mock_subprocess.assert_called_once_with(
        ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 40)"],
        check=True
    )

def test_dim_screen_failure(mock_subprocess):
    """Test handling of failure to dim screen."""
    # First call is from initialization
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    # Mock subprocess failure for the test call
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, "powershell")
    
    result = controller.dim_screen(40)
    
    assert result is False
    mock_subprocess.assert_called_once()

def test_restore_brightness_success(mock_subprocess):
    """Test successful restoration of original brightness."""
    # First call is from initialization
    controller = ScreenController()
    original_brightness = controller._original_brightness
    assert original_brightness == 75
    
    mock_subprocess.reset_mock()  # Reset after initialization
    
    result = controller.restore_brightness()
    
    assert result is True
    mock_subprocess.assert_called_once_with(
        ["powershell", "-Command", f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {original_brightness})"],
        check=True
    )

def test_restore_brightness_failure(mock_subprocess):
    """Test handling of failure to restore brightness."""
    # First call is from initialization
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    # Mock subprocess failure for the test call
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, "powershell")
    
    result = controller.restore_brightness()
    
    assert result is False
    mock_subprocess.assert_called_once()

def test_dim_screen_with_default_percentage(mock_subprocess):
    """Test dimming screen with default percentage."""
    # First call is from initialization
    controller = ScreenController()
    mock_subprocess.reset_mock()  # Reset after initialization
    
    result = controller.dim_screen()
    
    assert result is True
    mock_subprocess.assert_called_once_with(
        ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)"],
        check=True
    ) 