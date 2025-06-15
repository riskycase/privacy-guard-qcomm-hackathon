import subprocess
import os

class ScreenController:
    """
    Controls screen brightness on Windows systems.
    """
    def __init__(self):
        self._original_brightness = self._get_current_brightness()
        self._dimmed_brightness = 30  # Default dimmed brightness percentage
    
    def _get_current_brightness(self):
        """
        Get the current screen brightness using PowerShell.
        Returns the brightness as an integer percentage (0-100).
        """
        try:
            # PowerShell command to get current brightness
            cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=True
            )
            brightness = int(result.stdout.strip())
            return brightness
        except Exception as e:
            print(f"Error getting screen brightness: {e}")
            return 100  # Default to 100% if we can't get the current brightness
    
    def dim_screen(self, dim_percentage=None):
        """
        Dim the screen to the specified percentage.
        If dim_percentage is not provided, uses the default dimmed_brightness.
        """
        if dim_percentage is not None:
            self._dimmed_brightness = dim_percentage
        
        try:
            # PowerShell command to set brightness
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {self._dimmed_brightness})"
            subprocess.run(
                ["powershell", "-Command", cmd],
                check=True
            )
            return True
        except Exception as e:
            print(f"Error dimming screen: {e}")
            return False
    
    def restore_brightness(self):
        """
        Restore the screen brightness to its original value.
        """
        try:
            # PowerShell command to set brightness back to original
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {self._original_brightness})"
            subprocess.run(
                ["powershell", "-Command", cmd],
                check=True
            )
            return True
        except Exception as e:
            print(f"Error restoring screen brightness: {e}")
            return False
