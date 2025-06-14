import { MessageData, DOMData } from './types';

interface ExtendedDOMData extends DOMData {
  fullHTML: string;
  htmlSize: number;
  bodyHTML: string;
  headHTML: string;
}

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

    // Custom event listener for HTML requests
    window.addEventListener('REQUEST_FULL_HTML', () => {
      this.sendFullHTML();
    });

    // Initial DOM data send after page load
    if (document.readyState === 'complete') {
      setTimeout(() => {
        this.sendDOMData();
        this.sendFullHTML();
      }, 1000);
    } else {
      window.addEventListener('load', () => {
        setTimeout(() => {
          this.sendDOMData();
          this.sendFullHTML();
        }, 1000);
      });
    }

    // Monitor for dynamic changes (optional)
    this.setupDOMObserver();
  }

  private setupDOMObserver(): void {
    // Observer for significant DOM changes
    const observer = new MutationObserver((mutations) => {
      let significantChange = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Check if significant nodes were added
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const element = node as Element;
              if (element.tagName && ['DIV', 'SECTION', 'ARTICLE', 'MAIN'].includes(element.tagName)) {
                significantChange = true;
              }
            }
          });
        }
      });

      if (significantChange) {
        // Debounce the updates
        clearTimeout((this as any).domUpdateTimeout);
        (this as any).domUpdateTimeout = setTimeout(() => {
          this.sendDOMData();
        }, 2000);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false,
      characterData: false
    });
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

  private sendFullHTML(): void {
    const htmlData = this.extractFullHTML();
    
    console.log('Sending full HTML data:', {
      htmlSize: htmlData.htmlSize,
      url: window.location.href
    });
    
    this.sendMessage({
      type: 'FULL_HTML',
      data: htmlData,
      tabId: this.tabId,
      timestamp: Date.now()
    });
  }

  private extractFullHTML(): any {
    try {
      // Method 1: Get complete document HTML
      const fullHTML = document.documentElement.outerHTML;
      
      // Method 2: Using XMLSerializer (alternative approach)
      const serializer = new XMLSerializer();
      const serializedHTML = serializer.serializeToString(document);
      
      // Method 3: Get specific parts
      const headHTML = document.head.outerHTML;
      const bodyHTML = document.body.outerHTML;
      
      // Get rendered/computed styles for elements (optional)
      const computedStyles = this.getComputedStylesForImportantElements();

      return {
        fullHTML: fullHTML,
        serializedHTML: serializedHTML,
        headHTML: headHTML,
        bodyHTML: bodyHTML,
        htmlSize: fullHTML.length,
        url: window.location.href,
        title: document.title,
        timestamp: Date.now(),
        computedStyles: computedStyles,
        documentInfo: {
          readyState: document.readyState,
          characterSet: document.characterSet,
          contentType: document.contentType,
          lastModified: document.lastModified,
          domain: document.domain
        }
      };
    } catch (error) {
      console.error('Error extracting full HTML:', error);
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        url: window.location.href,
        timestamp: Date.now()
      };
    }
  }

  private getComputedStylesForImportantElements(): any {
    const importantElements: { [key: string]: any } = {};
    
    try {
      // Get styles for specific elements
      const selectors = ['body', 'main', '.container', '#main', 'article', 'section'];
      
      selectors.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
          const computedStyle = window.getComputedStyle(element);
          importantElements[selector] = {
            backgroundColor: computedStyle.backgroundColor,
            color: computedStyle.color,
            fontSize: computedStyle.fontSize,
            fontFamily: computedStyle.fontFamily,
            width: computedStyle.width,
            height: computedStyle.height,
            display: computedStyle.display,
            position: computedStyle.position
          };
        }
      });
    } catch (error) {
      console.error('Error getting computed styles:', error);
    }
    
    return importantElements;
  }

  private extractDOMData(): ExtendedDOMData {
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
    
    // Get full HTML
    const fullHTML = document.documentElement.outerHTML;
    const bodyHTML = document.body?.outerHTML || '';
    const headHTML = document.head?.outerHTML || '';

    return {
      title: document.title,
      url: window.location.href,
      domain: window.location.hostname,
      elementCount: document.querySelectorAll('*').length,
      imageCount: document.querySelectorAll('img').length,
      linkCount: document.querySelectorAll('a').length,
      textContent,
      metaTags,
      fullHTML,
      htmlSize: fullHTML.length,
      bodyHTML,
      headHTML
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