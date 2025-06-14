# Privacy Guard

A Python package to determine if a screen should be dimmed based on face detection and browser content sensitivity using an LLM.

## Agents
- **FaceDetectionAgent**: Pulls the number of faces from a REST API endpoint.
- **BrowserExtensionAgent**: Accepts JSON input with `url` and `dom` fields from a browser extension.
- **SensitivityChecker**: Uses a local LLM to determine if the content is sensitive.

## Logic
The screen will be dimmed if:
- More than 1 face is detected, **and**
- The browser content is sensitive (as determined by the LLM)

## Usage

```python
from privacy_guard.controller import should_dim_screen

# Example browser data from extension
browser_data = {
    "url": "https://example.com",
    "dom": "<html>...</html>"
}

if should_dim_screen(browser_data):
    # Dim the screen
    ...
```

## Configuration
Edit `privacy_guard/config.py` to set API endpoints as needed.

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