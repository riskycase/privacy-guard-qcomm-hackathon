import { MessageData, DOMData } from './types';

class ContentScriptMonitor {
  private tabId: number;

  constructor() {
    this.tabId = this.getTabId();
    this.setupEventListeners();
    this.sendPageLoadedMessage();
    console.log('Content script initialized for tab:', this.tabId);
  }

  private getTabId(): number {
    // Get tab ID from Chrome extension API if available
    return Math.floor(Math.random() * 1000000); // Fallback random ID
  }

  private setupEventListeners(): void {
    // Visibility change listener
    document.addEventListener('visibilitychange', () => {
      this.handleVisibilityChange();
    });

    // Custom event listener for DOM data requests
    window.addEventListener('REQUEST_DOM_DATA', () => {
      this.sendDOMData();
    });

    // Initial DOM data send after page load
    if (document.readyState === 'complete') {
      setTimeout(() => this.sendDOMData(), 1000);
    } else {
      window.addEventListener('load', () => {
        setTimeout(() => this.sendDOMData(), 1000);
      });
    }
  }

  private handleVisibilityChange(): void {
    const visibility = document.hidden ? 'hidden' : 'visible';
    
    console.log('Visibility changed:', visibility);
    
    this.sendMessage({
      type: 'VISIBILITY_CHANGE',
      data: { visibility },
      tabId: this.tabId,
      timestamp: Date.now()
    });
  }

  private sendPageLoadedMessage(): void {
    this.sendMessage({
      type: 'PAGE_LOADED',
      data: {
        url: window.location.href,
        title: document.title
      },
      tabId: this.tabId,
      timestamp: Date.now()
    });
  }

  private sendDOMData(): void {
    const domData = this.extractDOMData();
    
    console.log('Sending DOM data:', domData);
    
    this.sendMessage({
      type: 'DOM_DATA',
      data: domData,
      tabId: this.tabId,
      timestamp: Date.now()
    });
  }

  private extractDOMData(): DOMData {
    const metaTags: Record<string, string> = {};
    
    // Extract meta tags
    document.querySelectorAll('meta').forEach(meta => {
      const name = meta.getAttribute('name') || meta.getAttribute('property');
      const content = meta.getAttribute('content');
      if (name && content) {
        metaTags[name] = content;
      }
    });

    // Get text content (truncated for performance)
    const textContent = document.body?.innerText?.substring(0, 5000) || '';

    return {
      title: document.title,
      url: window.location.href,
      domain: window.location.hostname,
      elementCount: document.querySelectorAll('*').length,
      imageCount: document.querySelectorAll('img').length,
      linkCount: document.querySelectorAll('a').length,
      textContent,
      metaTags
    };
  }

  private sendMessage(message: MessageData): void {
    try {
      chrome.runtime.sendMessage(message);
    } catch (error) {
      console.error('Error sending message to background:', error);
    }
  }
}

// Initialize content script monitor
if (typeof window !== 'undefined') {
  new ContentScriptMonitor();
}