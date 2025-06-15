from typing import Dict

class BrowserExtensionAgent:
    def __init__(self, browser_data: Dict):
        self.browser_data = browser_data

    def get_browser_data(self) -> Dict:
        """
        Returns the browser data as a dict with 'url' and 'dom' keys.
        """
        url = self.browser_data.get('url', '')
        dom = self.browser_data.get('dom', '')
        return {'url': url, 'dom': dom} 