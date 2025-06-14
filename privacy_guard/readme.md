# Privacy Guard

A Python package to automatically dim the screen based on face detection and browser content sensitivity using an LLM.

## Agents
- **FaceDetectionAgent**: Pulls the number of faces from a REST API endpoint.
- **BrowserExtensionAgent**: Accepts JSON input with `url` and `dom` fields from a browser extension.
- **SensitivityChecker**: Uses a local LLM to determine if the content is sensitive.
- **ScreenController**: Controls screen brightness on Windows systems.

## Logic
The screen will be automatically dimmed if:
- More than 1 face is detected, **and**
- The browser content is sensitive (as determined by the LLM)

When these conditions are no longer met, the screen brightness will be restored to its original level.

## Usage

```python
from privacy_guard.controller import should_dim_screen, dim_screen, restore_brightness

# Example browser data from extension
browser_data = {
    "url": "https://example.com",
    "dom": "<html>...</html>"
}

# This will automatically dim the screen if conditions are met
# and restore brightness if conditions are not met
should_dim = should_dim_screen(browser_data)

# You can also manually control screen brightness
dim_screen(30)  # Dim to 30% brightness
restore_brightness()  # Restore to original brightness
```

## Configuration
The application uses environment variables for configuration. You can set these in a `.env` file in the privacy_guard directory.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set your API endpoints and authentication token:
   ```
   # API Endpoints
   FACE_API_URL=http://localhost:5000/api/faces
   LLM_URL=http://localhost:3001/api/v1/openai/chat/completions
   
   # API Authentication
   API_TOKEN=your_token_here
   ```

## LLM Prompt
The LLM is prompted with:

```
Given the following webpage content and URL, answer 'yes' if the content is sensitive (e.g., contains personal, financial, or confidential information), otherwise answer 'no'.
URL: {url}
Content: {dom}
Is the content sensitive? Answer 'yes' or 'no' only.
```

## Requirements
- Python 3.7+
- `requests` library
- `python-dotenv` library
- Windows operating system (for screen brightness control)

## Testing Screen Brightness Control

### PowerShell Test Script
A PowerShell script is included to test screen brightness control functionality without running the full Privacy Guard package:

```powershell
# Run from PowerShell with administrator privileges
.\test_screen_brightness.ps1
```

This script will:
1. Get the current screen brightness
2. Ask for confirmation to dim the screen to 30%
3. If confirmed, dim the screen for 3 seconds
4. Restore the original brightness

### Example Python Script
An example Python script is included to demonstrate how to use the Privacy Guard package:

```bash
python -m privacy_guard.example
```

This script demonstrates:
- Checking if the screen should be dimmed based on browser data
- Manually controlling screen brightness
- Restoring screen brightness to its original level
