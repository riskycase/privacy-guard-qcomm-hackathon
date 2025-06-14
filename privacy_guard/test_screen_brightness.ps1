# PowerShell script to test screen brightness control on Windows

# Function to get current brightness
function Get-ScreenBrightness {
    try {
        $brightness = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness
        return $brightness
    }
    catch {
        Write-Host "Error getting screen brightness: $_"
        return $null
    }
}

# Function to set screen brightness
function Set-ScreenBrightness {
    param (
        [int]$BrightnessLevel
    )
    
    try {
        (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, $BrightnessLevel)
        return $true
    }
    catch {
        Write-Host "Error setting screen brightness: $_"
        return $false
    }
}

# Main script
Write-Host "Screen Brightness Control Test"
Write-Host "============================"

# Get current brightness
$originalBrightness = Get-ScreenBrightness
Write-Host "Current screen brightness: $originalBrightness%"

# Ask user for confirmation before changing brightness
$confirmation = Read-Host "Do you want to dim the screen to 30% brightness? (y/n)"
if ($confirmation -eq 'y') {
    Write-Host "Dimming screen to 30%..."
    Set-ScreenBrightness -BrightnessLevel 30
    
    Start-Sleep -Seconds 3
    
    Write-Host "Restoring original brightness ($originalBrightness%)..."
    Set-ScreenBrightness -BrightnessLevel $originalBrightness
    
    Write-Host "Test completed."
}
else {
    Write-Host "Test cancelled."
}
