import { TabData, MessageData, DOMData } from './types';

class TabMonitor {
  private currentTabId: number | null = null;
  private tabDataLog: TabData[] = [];

  constructor() {
    this.setupEventListeners();
    console.log('Tab Monitor Extension: Background script initialized');
  }

  private setupEventListeners(): void {
    // Tab activation changes
    chrome.tabs.onActivated.addListener((activeInfo) => {
      this.handleTabActivated(activeInfo.tabId);
    });

    // Tab updates (URL changes, loading states)
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url) {
        this.handleTabUpdated(tabId, tab);
      }
    });

    // Messages from content script
    chrome.runtime.onMessage.addListener((message: MessageData, sender, sendResponse) => {
      this.handleContentMessage(message, sender);
      sendResponse({ success: true });
    });

    // Window focus changes
    chrome.windows.onFocusChanged.addListener((windowId) => {
      if (windowId !== chrome.windows.WINDOW_ID_NONE) {
        this.handleWindowFocusChanged(windowId);
      }
    });
  }

  private async handleTabActivated(tabId: number): Promise<void> {
    this.currentTabId = tabId;
    
    try {
      const tab = await chrome.tabs.get(tabId);
      console.log('Tab activated:', {
        tabId,
        url: tab.url,
        title: tab.title,
        timestamp: Date.now()
      });

      await this.captureTabData(tab);
    } catch (error) {
      console.error('Error handling tab activation:', error);
    }
  }

  private async handleTabUpdated(tabId: number, tab: chrome.tabs.Tab): Promise<void> {
    console.log('Tab updated:', {
      tabId,
      url: tab.url,
      title: tab.title,
      timestamp: Date.now()
    });

    await this.captureTabData(tab);
  }

  private async handleWindowFocusChanged(windowId: number): Promise<void> {
    try {
      const tabs = await chrome.tabs.query({ active: true, windowId });
      if (tabs.length > 0) {
        this.handleTabActivated(tabs[0].id!);
      }
    } catch (error) {
      console.error('Error handling window focus change:', error);
    }
  }

  private handleContentMessage(message: MessageData, sender: chrome.runtime.MessageSender): void {
    const tabId = sender.tab?.id;
    if (!tabId) return;

    console.log('Message from content script:', {
      type: message.type,
      tabId,
      timestamp: message.timestamp
    });

    switch (message.type) {
      case 'DOM_DATA':
        this.updateTabDataWithDOM(tabId, message.data);
        break;
      case 'VISIBILITY_CHANGE':
        this.logVisibilityChange(tabId, message.data.visibility);
        break;
      case 'PAGE_LOADED':
        this.handlePageLoaded(tabId);
        break;
    }
  }

  private async captureTabData(tab: chrome.tabs.Tab): Promise<void> {
    if (!tab.id || !tab.url) return;

    try {
      const screenshot = await this.captureScreenshot(tab.id);
      
      const tabData: TabData = {
        url: tab.url,
        title: tab.title || '',
        tabId: tab.id,
        timestamp: Date.now(),
        screenshot,
        visibility: 'visible'
      };

      this.tabDataLog.push(tabData);
      this.logTabData(tabData);

      // Request DOM data from content script
      await this.requestDOMData(tab.id);

    } catch (error) {
      console.error('Error capturing tab data:', error);
    }
  }

  private async captureScreenshot(tabId: number): Promise<string | undefined> {
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(undefined, {
        format: 'png',
        quality: 80
      });
      return dataUrl;
    } catch (error) {
      console.error('Error capturing screenshot:', error);
      return undefined;
    }
  }

  private async requestDOMData(tabId: number): Promise<void> {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          // This will trigger the content script to send DOM data
          window.dispatchEvent(new CustomEvent('REQUEST_DOM_DATA'));
        }
      });
    } catch (error) {
      console.error('Error requesting DOM data:', error);
    }
  }

  private updateTabDataWithDOM(tabId: number, domData: DOMData): void {
    const latestTabData = this.tabDataLog
      .filter(data => data.tabId === tabId)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    if (latestTabData) {
      latestTabData.domData = domData;
      console.log('Updated tab data with DOM:', {
        tabId,
        url: latestTabData.url,
        domData
      });
    }
  }

  private logVisibilityChange(tabId: number, visibility: 'visible' | 'hidden'): void {
    console.log('Visibility changed:', {
      tabId,
      visibility,
      timestamp: Date.now()
    });

    // Update latest tab data
    const latestTabData = this.tabDataLog
      .filter(data => data.tabId === tabId)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    if (latestTabData) {
      latestTabData.visibility = visibility;
    }
  }

  private handlePageLoaded(tabId: number): void {
    console.log('Page loaded:', { tabId, timestamp: Date.now() });
  }

  private logTabData(tabData: TabData): void {
    console.log('=== TAB DATA LOG ===');
    console.log('URL:', tabData.url);
    console.log('Title:', tabData.title);
    console.log('Tab ID:', tabData.tabId);
    console.log('Timestamp:', new Date(tabData.timestamp).toISOString());
    console.log('Screenshot length:', tabData.screenshot?.length || 0);
    console.log('Visibility:', tabData.visibility);
    if (tabData.domData) {
      console.log('DOM Data:', tabData.domData);
    }
    console.log('==================');
  }

  // Public method to get logged data
  public getTabDataLog(): TabData[] {
    return this.tabDataLog;
  }
}

// Initialize the tab monitor
const tabMonitor = new TabMonitor();

// Make it accessible globally for debugging
(globalThis as any).tabMonitor = tabMonitor;