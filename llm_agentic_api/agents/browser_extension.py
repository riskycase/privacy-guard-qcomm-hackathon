from typing import Dict, Any

def process_browser_extension_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes input from the browser extension. Expects a dict with 'url' and 'dom'.
    For now, just returns the input.
    """
    url = data.get("url")
    dom = data.get("dom")
    return {"url": url, "dom": dom} 