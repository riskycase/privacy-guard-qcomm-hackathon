# Unified Privacy Guard System

A comprehensive privacy protection system that automatically dims your screen when multiple people are detected and sensitive content is being viewed.

## 🎯 Overview

This system integrates multiple components to provide intelligent privacy protection:

- **🎥 Face Detection**: Uses camera to detect number of people present
- **🌐 Browser Monitoring**: Captures current webpage content and metadata
- **🤖 AI Content Analysis**: Uses LLM to determine if content is sensitive
- **💡 Screen Control**: Automatically dims screen brightness when privacy is needed

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Browser Ext.   │───▶│  Central Server │───▶│                 │
│  (Data Capture) │    │  (Data Storage) │    │                 │
└─────────────────┘    └─────────────────┘    │                 │
                                              │  Unified        │
┌─────────────────┐    ┌─────────────────┐    │  Privacy        │
│  Face Detection │───▶│  Face Count API │───▶│  Guard          │
│  (Camera/ONNX)  │    │  (FastAPI)      │    │                 │
└─────────────────┘    └─────────────────┘    │                 │
                                              │                 │
┌─────────────────┐                           │                 │
│  LLM Service    │◀──────────────────────────│                 │
│  (Sensitivity)  │                           └─────────────────┘
└─────────────────┘                                    │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Screen Control  │
                                              │ (Brightness)    │
                                              └─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install requests python-dotenv aiohttp opencv-python onnxruntime fastapi uvicorn

# Node.js dependencies (for central server)
cd central-server
npm install
cd ..
```

### 2. Set Up Environment

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

### 3. Start All Services

```bash
# Start everything at once (requires ONNX model file)
python start_privacy_guard.py --model-path /path/to/your/model.onnx

# Or start services individually
python start_privacy_guard.py --server-only    # Central server only
python start_privacy_guard.py --face-only --model-path /path/to/model.onnx  # Face detection only
python start_privacy_guard.py --guard-only     # Privacy guard only
```

### 4. Load Browser Extension

1. Open your browser (Chrome/Edge)
2. Go to Extensions → Developer Mode
3. Load the `browser-extension` folder
4. Ensure it's configured to send data to `http://localhost:3000/api/storage`

## 📁 Project Structure

```
privacy-guard-qcomm-hackathon/
├── 📄 unified_privacy_guard.py      # Main unified script
├── 📄 start_privacy_guard.py        # Service launcher
├── 📄 UNIFIED_SETUP_GUIDE.md        # Detailed setup guide
├── 📄 README_UNIFIED.md             # This file
├── 
├── 🌐 browser-extension/            # Browser extension
│   ├── src/background.ts            # Extension background script
│   ├── src/content.ts               # Content script
│   └── manifest.json                # Extension manifest
├── 
├── 🖥️ central-server/               # Data storage server
│   ├── src/server.ts                # Express server
│   └── src/routes/storage.ts        # Storage API routes
├── 
├── 👁️ face-detect/                  # Face detection system
│   └── face_counter/
│       ├── detector.py              # ONNX face detector
│       ├── camera_handler.py        # Camera interface
│       └── api_server.py            # FastAPI server
├── 
├── 🤖 LLM/                          # LLM integration
│   └── readme.md                    # LLM setup instructions
├── 
└── 🛡️ privacy_guard/                # Privacy control logic
    ├── controller.py                # Main controller
    ├── screen_control.py            # Screen brightness control
    ├── llm/sensitivity_checker.py   # LLM integration
    └── agents/                      # Data source agents
        ├── browser_extension.py     # Browser data agent
        └── face_detection.py        # Face detection agent
```

## 🔧 Configuration Options

### Unified Privacy Guard

```bash
python unified_privacy_guard.py \
    --face-api-url http://127.0.0.1:8000/face-count \
    --browser-server-url http://localhost:3000/api/storage \
    --llm-url http://localhost:3001/api/v1/openai/chat/completions \
    --check-interval 2.0
```

### Service Launcher

```bash
python start_privacy_guard.py \
    --model-path /path/to/model.onnx \
    --face-api-host 127.0.0.1 \
    --face-api-port 8000 \
    --server-port 3000 \
    --check-interval 2.0
```

## 🎛️ How It Works

### Decision Logic

The system dims the screen when **BOTH** conditions are met:

1. **👥 Multiple Faces**: More than 1 face detected by camera
2. **🔒 Sensitive Content**: LLM determines current browser content is sensitive

### Content Sensitivity Detection

The LLM analyzes:
- Current webpage URL
- Page title  
- DOM text content

Content is considered sensitive if it contains:
- Personal information (names, addresses, phone numbers)
- Financial data (bank accounts, credit cards, transactions)
- Confidential information (passwords, private documents)
- Private communications (emails, messages, personal photos)

### Screen Brightness Control

- **Dimming**: Reduces brightness to 30% (configurable)
- **Restoration**: Returns to original brightness when conditions change
- **State Tracking**: Remembers original brightness and current state

## 🔍 Testing & Debugging

### Test Individual Components

```bash
# Test face detection API
curl http://127.0.0.1:8000/face-count

# Test browser data storage
curl http://localhost:3000/api/storage/latest_tab_event

# Test unified system once
python unified_privacy_guard.py --test-once

# Check service status
python start_privacy_guard.py --status
```

### Enable Debug Logging

Modify the logging level in `unified_privacy_guard.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Screen brightness not changing | Run as administrator, check WMI services |
| Face detection not working | Verify camera permissions, ONNX model path |
| Browser data not available | Check extension is loaded, central server running |
| LLM sensitivity check failing | Verify LLM service, API token, network connectivity |

### Service Dependencies

Ensure services start in this order:
1. **Face Detection Service** (requires ONNX model)
2. **Central Server** (requires Node.js)
3. **LLM Service** (external service)
4. **Browser Extension** (load in browser)
5. **Unified Privacy Guard** (main script)

## 🔐 Security Considerations

- **Data Privacy**: Browser content is processed locally and via configured LLM
- **Camera Access**: Required for face detection
- **System Access**: Screen brightness control requires system permissions
- **Network**: Multiple services communicate over localhost

## 📊 Performance

- **Check Interval**: Default 2 seconds (configurable)
- **LLM Calls**: Only when browser content changes
- **Face Detection**: Continuous camera processing
- **Screen Control**: Immediate brightness changes

## 🎨 Customization

### Adjust Sensitivity Threshold

Modify the LLM prompt in `SensitivityChecker` class:

```python
system_prompt = (
    "You are a helpful assistant that determines if web content is sensitive. "
    "Modify this prompt to change sensitivity criteria..."
)
```

### Change Dim Percentage

Modify `_dimmed_brightness` in `ScreenController` class:

```python
self._dimmed_brightness = 20  # Change from default 30%
```

### Add New Content Sources

Extend `BrowserDataClient` to handle additional browser events or data sources.

## 📝 Usage Examples

### Basic Usage
```bash
# Start all services with model
python start_privacy_guard.py --model-path ./model.onnx
```

### Development Mode
```bash
# Start services individually for development
python start_privacy_guard.py --server-only &
python start_privacy_guard.py --face-only --model-path ./model.onnx &
python unified_privacy_guard.py --test-once
```

### Custom Configuration
```bash
# Custom ports and intervals
python start_privacy_guard.py \
    --model-path ./model.onnx \
    --face-api-port 8001 \
    --server-port 3001 \
    --check-interval 1.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `--test-once` mode
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs with debug mode enabled
3. Test individual components
4. Create an issue with detailed information

---

**⚠️ Important**: This system requires camera access, system permissions for brightness control, and processes browser content. Ensure you understand the privacy and security implications before deployment.
