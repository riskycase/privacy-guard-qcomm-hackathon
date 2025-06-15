# Unified Privacy Guard Setup Guide

This guide explains how to set up and run the unified privacy guard script that integrates all components of the privacy guard system.

## Overview

The unified script (`unified_privacy_guard.py`) combines:
- **Browser Extension + Central Server**: Captures browser data (URL, DOM, screenshots)
- **Face Detection**: Detects number of faces using camera
- **LLM Sensitivity Analysis**: Analyzes content for sensitive information
- **Screen Brightness Control**: Automatically dims screen when conditions are met

## Prerequisites

### 1. Python Dependencies
```bash
pip install requests python-dotenv aiohttp
```

### 2. System Requirements
- **Windows**: The script uses PowerShell commands for screen brightness control
- **Camera**: Required for face detection
- **ONNX Model**: Face detection model file

## Component Setup

### 1. Face Detection Service
Start the face detection API server:
```bash
cd face-detect
python -m face_counter --model-path /path/to/your/model.onnx --api-host 127.0.0.1 --api-port 8000
```

### 2. Central Server (Browser Data)
Start the central server for browser extension data:
```bash
cd central-server
npm install
npm start
```
This runs on `http://localhost:3000` by default.

### 3. Browser Extension
1. Load the browser extension in your browser
2. Ensure it's configured to send data to `http://localhost:3000/api/storage`

### 4. LLM Service
Ensure your LLM service is running on the configured endpoint (default: `http://localhost:3001/api/v1/openai/chat/completions`)

## Environment Configuration

Create a `.env` file in the project root:
```env
# Face Detection API
FACE_API_URL=http://127.0.0.1:8000/face-count

# Browser Extension Central Server
BROWSER_SERVER_URL=http://localhost:3000/api/storage

# LLM Configuration
LLM_URL=http://localhost:3001/api/v1/openai/chat/completions
API_TOKEN=your_api_token_here
WORKSPACE_NAME=your_workspace_name
```

## Running the Unified Script

### Basic Usage
```bash
python unified_privacy_guard.py
```

### With Custom Configuration
```bash
python unified_privacy_guard.py \
    --face-api-url http://127.0.0.1:8000/face-count \
    --browser-server-url http://localhost:3000/api/storage \
    --llm-url http://localhost:3001/api/v1/openai/chat/completions \
    --check-interval 2.0
```

### Test Mode (Single Check)
```bash
python unified_privacy_guard.py --test-once
```

## How It Works

### Decision Logic
The script automatically dims the screen when **BOTH** conditions are met:
1. **Multiple Faces Detected**: More than 1 face is detected by the camera
2. **Sensitive Content**: The LLM determines the current browser content is sensitive

### Content Sensitivity Analysis
The LLM analyzes:
- Current webpage URL
- Page title
- DOM content (text content from the page)

Content is considered sensitive if it contains:
- Personal information
- Financial data
- Confidential information
- Private communications

### Screen Control
- **Dimming**: Screen brightness is reduced to 30% (configurable)
- **Restoration**: Screen brightness is restored to original level when conditions are no longer met
- **State Tracking**: The script remembers the original brightness and current dimmed state

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--face-api-url` | `http://127.0.0.1:8000/face-count` | Face detection API endpoint |
| `--browser-server-url` | `http://localhost:3000/api/storage` | Browser data server endpoint |
| `--llm-url` | `http://localhost:3001/api/v1/openai/chat/completions` | LLM API endpoint |
| `--check-interval` | `2.0` | Check interval in seconds |
| `--test-once` | `False` | Run once and exit (for testing) |

## Startup Sequence

To run the complete system:

1. **Start Face Detection Service**:
   ```bash
   cd face-detect
   python -m face_counter --model-path /path/to/model.onnx
   ```

2. **Start Central Server**:
   ```bash
   cd central-server
   npm start
   ```

3. **Start LLM Service** (if not already running)

4. **Load Browser Extension** in your browser

5. **Start Unified Privacy Guard**:
   ```bash
   python unified_privacy_guard.py
   ```

## Troubleshooting

### Common Issues

1. **Screen brightness control not working**:
   - Ensure you're running on Windows
   - Run PowerShell as administrator if needed
   - Check if WMI services are running

2. **Face detection API not responding**:
   - Verify the face detection service is running
   - Check camera permissions
   - Ensure ONNX model file exists

3. **Browser data not available**:
   - Verify central server is running
   - Check browser extension is loaded and active
   - Ensure extension is sending data to correct endpoint

4. **LLM sensitivity check failing**:
   - Verify LLM service is running
   - Check API token and workspace configuration
   - Review network connectivity

### Logging

The script provides detailed logging. To see debug information:
```python
# Modify logging level in the script
logging.basicConfig(level=logging.DEBUG)
```

### Testing Individual Components

Test each component separately:

```bash
# Test face detection
curl http://127.0.0.1:8000/face-count

# Test browser data
curl http://localhost:3000/api/storage/latest_tab_event

# Test LLM (requires proper headers)
curl -X POST http://localhost:3001/api/v1/openai/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"your_model","messages":[{"role":"user","content":"test"}]}'
```

## Security Considerations

- The script processes sensitive browser data
- Screen brightness changes are system-level operations
- Camera access is required for face detection
- Network communication with multiple services

Ensure all services are running on trusted networks and properly secured.

## Performance Notes

- Default check interval is 2 seconds (configurable)
- LLM calls are made only when content changes
- Face detection runs continuously
- Screen brightness changes are immediate

## Customization

### Adjusting Sensitivity Threshold
Modify the LLM prompt in the `SensitivityChecker` class to change what's considered sensitive.

### Changing Dim Percentage
Modify the `_dimmed_brightness` value in the `ScreenController` class (default: 30%).

### Adding New Data Sources
Extend the `BrowserDataClient` class to handle additional browser extension events.
