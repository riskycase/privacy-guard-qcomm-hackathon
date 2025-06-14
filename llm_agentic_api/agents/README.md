# Agents

This folder contains agent modules for the LLM Agentic API.

## Included Agents
- `face_detection.py`: Calls a face detection API to count faces in an image.
- `browser_extension.py`: Processes input from a browser extension (URL and DOM).

## Adding New Agents
1. Create a new Python file in this folder (e.g., `my_agent.py`).
2. Implement your agent's logic as an async function or class.
3. Register your agent as a tool/function in `main.py`.

See the main [README](../README.md) for setup, environment, and usage instructions. 