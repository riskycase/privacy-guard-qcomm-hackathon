# LLM Agentic API

This package exposes an API endpoint for a local LLM (via LM Studio) with agentic capabilities.

## Agents
- **Face-detection agent**: Calls a configurable API to get the number of faces in an image.
- **Browser-extension agent**: Accepts JSON input with URL and HTML DOM from a browser extension.

## Requirements
- Python 3.8+
- LM Studio running locally (OpenAI-compatible endpoint)
- Face detection API endpoint

## Installation
```bash
pip install -r requirements.txt
```

## Environment Setup
You can use a `.env` file or set environment variables directly.

### Option A: Using a `.env` file
Create a file named `.env` in your project root with:
```
LMSTUDIO_API_URL=http://localhost:1234/v1
FACE_DETECTION_API_URL=http://localhost:8001/face-detect
```
To load these automatically, install `python-dotenv` and add this to the top of `main.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```
And add `python-dotenv` to your `requirements.txt`.

### Option B: Export in your shell
```bash
export LMSTUDIO_API_URL=http://localhost:1234/v1
export FACE_DETECTION_API_URL=http://localhost:8001/face-detect
```

## Running the API
Start LM Studio and your face detection API first. Then run:
```bash
uvicorn llm_agentic_api.main:app --reload
```
- The API will be available at: `http://127.0.0.1:8000/v1/agentic-chat`

## Example Requests

### Face Detection Agent
```bash
curl -X POST http://127.0.0.1:8000/v1/agentic-chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How many faces are in this image?",
    "face_image_url": "https://example.com/image.jpg"
  }'
```

### Browser Extension Agent
```bash
curl -X POST http://127.0.0.1:8000/v1/agentic-chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the title of the current web page?",
    "browser_data": {
      "url": "https://example.com",
      "dom": "<html><head><title>Example Domain</title></head><body>...</body></html>"
    }
  }'
```

## Testing
- Use the `/docs` endpoint (Swagger UI) at `http://127.0.0.1:8000/docs` to interactively test your API.

## Troubleshooting
- If you get connection errors, check that LM Studio and the face detection API are running and accessible.
- If you get CORS errors, add CORS middleware to your FastAPI app:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

## Next Steps
- Add more agents as needed.
- Improve prompt engineering for better LLM responses.
- Deploy on your target hardware (Windows/WSL/Qualcomm NPU).

## Configuration
- Set the LM Studio and face detection API URLs in environment variables or `.env` file:
  - `LMSTUDIO_API_URL`
  - `FACE_DETECTION_API_URL`

## Usage
- POST to `/v1/agentic-chat` with your prompt and (optionally) agent inputs. 

## Multi-Step Agent Orchestration

The API supports multi-step tool use: the LLM can call multiple agents in sequence, and the API will loop, handling each tool call and returning the final answer.

## Deployment

- **Local (Windows/WSL):** Start LM Studio and the API as described above. Use the correct host/IP for LM Studio if running across WSL/Windows.
- **Qualcomm NPU:** Ensure LM Studio and/or your face detection API are configured to use the NPU.
- **Production:** Use a production ASGI server, process manager, and HTTPS. Secure your endpoints as needed.