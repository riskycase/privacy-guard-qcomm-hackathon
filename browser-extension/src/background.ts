import { TabData, MessageData, DOMData } from "./types";

interface ServerConfig {
  baseUrl: string;
  enabled: boolean;
  retryAttempts: number;
  retryDelay: number;
  singleKey: string;
}

interface MonitorEvent {
  id: string;
  event: string;
  timestamp: number;
  data: any;
}

class TabMonitor {
  private currentTabId: number | null = null;
  private tabDataLog: TabData[] = [];
  private serverConfig: ServerConfig = {
    baseUrl: "http://localhost:3000/api/storage",
    enabled: true,
    retryAttempts: 3,
    retryDelay: 1000,
    singleKey: "latest_tab_event",
  };
  private isProcessingUpdate = false;
  private eventQueue: MonitorEvent[] = [];

  constructor() {
    this.setupEventListeners();
    this.loadServerConfig();
    this.sendInitialEvent();
    console.log("Tab Monitor Extension: Background script initialized");
  }

  private async sendInitialEvent(): Promise<void> {
    const initEvent: MonitorEvent = {
      id: this.generateEventId(),
      event: "extension_started",
      timestamp: Date.now(),
      data: {
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
      },
    };

    await this.sendEventToServer(initEvent);
    console.log("Extension started event sent");
  }

  private generateEventId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private shouldIgnoreUrl(url: string | undefined): boolean {
    if (!url) return true;

    const ignoredPrefixes = [
      "chrome://",
      "chrome-extension://",
      "moz-extension://",
      "edge://",
      "about:",
      "data:",
      "blob:",
    ];

    return ignoredPrefixes.some((prefix) => url.startsWith(prefix));
  }

  private async loadServerConfig(): Promise<void> {
    try {
      const result = await chrome.storage.sync.get(["serverConfig"]);
      if (result.serverConfig) {
        this.serverConfig = { ...this.serverConfig, ...result.serverConfig };
      }
      console.log("Server config loaded:", this.serverConfig);
    } catch (error) {
      console.error("Error loading server config:", error);
    }
  }

  private async saveServerConfig(): Promise<void> {
    try {
      await chrome.storage.sync.set({ serverConfig: this.serverConfig });
    } catch (error) {
      console.error("Error saving server config:", error);
    }
  }

  private setupEventListeners(): void {
    // Tab activation changes
    chrome.tabs.onActivated.addListener((activeInfo) => {
      this.handleTabActivated(activeInfo.tabId);
    });

    // Tab updates (URL changes, loading states)
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (
        changeInfo.status === "complete" &&
        tab.url &&
        !this.shouldIgnoreUrl(tab.url)
      ) {
        this.handleTabUpdated(tabId, tab);
      }
    });

    // Messages from content script
    chrome.runtime.onMessage.addListener(
      (message: MessageData, sender, sendResponse) => {
        // Check if the sender tab URL should be ignored
        if (this.shouldIgnoreUrl(sender.tab?.url)) {
          sendResponse({ success: true, ignored: true });
          return;
        }

        this.handleContentMessage(message, sender);
        sendResponse({ success: true });
      }
    );

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

      // Skip chrome:// URLs
      if (this.shouldIgnoreUrl(tab.url)) {
        console.log("Ignoring chrome:// URL:", tab.url);
        return;
      }

      const event: MonitorEvent = {
        id: this.generateEventId(),
        event: "tab_activated",
        timestamp: Date.now(),
        data: {
          tabId,
          url: tab.url,
          title: tab.title,
        },
      };

      console.log("Tab activated:", event.data);
      await this.sendEventToServer(event);

      await this.captureTabData(tab);
    } catch (error) {
      console.error("Error handling tab activation:", error);
    }
  }

  private async handleTabUpdated(
    tabId: number,
    tab: chrome.tabs.Tab
  ): Promise<void> {
    // Skip chrome:// URLs
    if (this.shouldIgnoreUrl(tab.url)) {
      console.log("Ignoring chrome:// URL update:", tab.url);
      return;
    }

    const event: MonitorEvent = {
      id: this.generateEventId(),
      event: "tab_updated",
      timestamp: Date.now(),
      data: {
        tabId,
        url: tab.url,
        title: tab.title,
      },
    };

    console.log("Tab updated:", event.data);
    await this.sendEventToServer(event);

    await this.captureTabData(tab);
  }

  private async handleWindowFocusChanged(windowId: number): Promise<void> {
    try {
      const tabs = await chrome.tabs.query({ active: true, windowId });
      if (tabs.length > 0) {
        // Skip chrome:// URLs
        if (this.shouldIgnoreUrl(tabs[0].url)) {
          console.log("Ignoring chrome:// URL focus change:", tabs[0].url);
          return;
        }

        const event: MonitorEvent = {
          id: this.generateEventId(),
          event: "window_focus_changed",
          timestamp: Date.now(),
          data: {
            windowId,
            tabId: tabs[0].id,
            url: tabs[0].url,
            title: tabs[0].title,
          },
        };

        console.log("Window focus changed:", event.data);
        await this.sendEventToServer(event);

        this.handleTabActivated(tabs[0].id!);
      }
    } catch (error) {
      console.error("Error handling window focus change:", error);
    }
  }

  private async captureTabData(tab: chrome.tabs.Tab): Promise<void> {
    if (!tab.id || !tab.url || this.shouldIgnoreUrl(tab.url)) return;

    try {
      const screenshot = await this.captureScreenshot(tab.id);

      const tabData: TabData = {
        url: tab.url,
        title: tab.title || "",
        tabId: tab.id,
        timestamp: Date.now(),
        screenshot,
        visibility: "visible",
      };

      this.tabDataLog.push(tabData);
      this.logTabData(tabData);

      // Create event for tab data capture
      const event: MonitorEvent = {
        id: this.generateEventId(),
        event: "tab_data_captured",
        timestamp: Date.now(),
        data: {
          tabId: tab.id,
          url: tab.url,
          title: tab.title || "",
          screenshotSize: screenshot?.length || 0,
          screenshot: screenshot,
          visibility: "visible",
        },
      };

      await this.sendEventToServer(event);

      // Request DOM data from content script
      await this.requestDOMData(tab.id);
    } catch (error) {
      console.error("Error capturing tab data:", error);

      const errorEvent: MonitorEvent = {
        id: this.generateEventId(),
        event: "capture_error",
        timestamp: Date.now(),
        data: {
          tabId: tab.id,
          url: tab.url,
          error: error instanceof Error ? error.message : "Unknown error",
        },
      };

      await this.sendEventToServer(errorEvent);
    }
  }

  private async captureScreenshot(tabId: number): Promise<string | undefined> {
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab({
        format: "png",
        quality: 80,
      });
      return dataUrl;
    } catch (error) {
      console.error("Error capturing screenshot:", error);
      return undefined;
    }
  }

  private async requestDOMData(tabId: number): Promise<void> {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          window.dispatchEvent(new CustomEvent("REQUEST_DOM_DATA"));
        },
      });
    } catch (error) {
      console.error("Error requesting DOM data:", error);
    }
  }

  private async updateTabDataWithDOM(
    tabId: number,
    domData: DOMData
  ): Promise<void> {
    const latestTabData = this.tabDataLog
      .filter((data) => data.tabId === tabId)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    if (latestTabData) {
      latestTabData.domData = domData;

      const event: MonitorEvent = {
        id: this.generateEventId(),
        event: "dom_data_updated",
        timestamp: Date.now(),
        data: {
          tabId,
          url: latestTabData.url,
          domData,
        },
      };

      console.log("Updated tab data with DOM:", event.data);
      await this.sendEventToServer(event);
    }
  }

  private async logVisibilityChange(
    tabId: number,
    visibility: "visible" | "hidden"
  ): Promise<void> {
    const event: MonitorEvent = {
      id: this.generateEventId(),
      event: "visibility_changed",
      timestamp: Date.now(),
      data: {
        tabId,
        visibility,
      },
    };

    console.log("Visibility changed:", event.data);
    await this.sendEventToServer(event);

    // Update latest tab data
    const latestTabData = this.tabDataLog
      .filter((data) => data.tabId === tabId)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    if (latestTabData) {
      latestTabData.visibility = visibility;
    }
  }

  private async handlePageLoaded(tabId: number, url?: string): Promise<void> {
    const event: MonitorEvent = {
      id: this.generateEventId(),
      event: "page_loaded",
      timestamp: Date.now(),
      data: {
        tabId,
        url,
      },
    };

    console.log("Page loaded:", event.data);
    await this.sendEventToServer(event);
  }

  private logTabData(tabData: TabData): void {
    console.log("=== TAB DATA LOG ===");
    console.log("URL:", tabData.url);
    console.log("Title:", tabData.title);
    console.log("Tab ID:", tabData.tabId);
    console.log("Timestamp:", new Date(tabData.timestamp).toISOString());
    console.log("Screenshot length:", tabData.screenshot?.length || 0);
    console.log("Visibility:", tabData.visibility);
    if (tabData.domData) {
      console.log("DOM Data:", tabData.domData);
    }
    console.log("==================");
  }

  // Server communication method
  private async sendEventToServer(event: MonitorEvent): Promise<void> {
    if (!this.serverConfig.enabled) {
      console.log("Server communication disabled, skipping:", event.event);
      return;
    }

    if (this.isProcessingUpdate) {
      console.log("Already processing an event, queuing:", event.event);
      this.eventQueue.push(event);
      return;
    }

    this.isProcessingUpdate = true;

    try {
      await this.sendEventWithRetry(event);
    } finally {
      this.isProcessingUpdate = false;
      this.processEventQueue();
    }
  }

  // Process queued events
  private async processEventQueue(): Promise<void> {
    if (this.eventQueue.length === 0 || this.isProcessingUpdate) {
      return;
    }

    const nextEvent = this.eventQueue.shift();
    if (nextEvent) {
      console.log(`Processing queued event: ${nextEvent.event} (${nextEvent.id})`);
      await this.sendEventToServer(nextEvent);
    }
  }

  private async sendEventWithRetry(
    event: MonitorEvent,
    attempt: number = 1
  ): Promise<void> {
    try {
      const response = await fetch(
        `${this.serverConfig.baseUrl}/${this.serverConfig.singleKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ data: event }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log(
        `✅ Event sent to server - ${event.event} (${event.id})`,
        result
      );
    } catch (error) {
      console.error(
        `❌ Failed to send event to server (attempt ${attempt}/${this.serverConfig.retryAttempts}):`,
        error
      );

      if (attempt < this.serverConfig.retryAttempts) {
        // Retry after delay
        setTimeout(() => {
          this.sendEventWithRetry(event, attempt + 1);
        }, this.serverConfig.retryDelay * attempt);
      } else {
        console.error(
          `❌ Failed to send event after ${this.serverConfig.retryAttempts} attempts:`,
          { event: event.event, id: event.id, error }
        );
      }
    }
  }

  // Public methods for configuration
  public updateServerConfig(config: Partial<ServerConfig>): void {
    this.serverConfig = { ...this.serverConfig, ...config };
    this.saveServerConfig();
    console.log("Server config updated:", this.serverConfig);
  }

  public getServerStats(): any {
    return {
      config: this.serverConfig,
      isProcessing: this.isProcessingUpdate,
      totalTabDataEntries: this.tabDataLog.length,
      queuedEvents: this.eventQueue.length,
      queueStatus: this.eventQueue.length > 0 ? 'Events queued' : 'Queue empty'
    };
  }

  public getTabDataLog(): TabData[] {
    return this.tabDataLog;
  }

  // Method to test server connection
  public async testServerConnection(): Promise<boolean> {
    try {
      const response = await fetch(
        `${this.serverConfig.baseUrl.replace("/api/storage", "")}/health`
      );
      const result = await response.json();

      console.log("Server connection test:", result);
      return response.ok;
    } catch (error) {
      console.error("Server connection test failed:", error);
      return false;
    }
  }

  // Method to manually send a test event
  public async sendTestEvent(): Promise<void> {
    const testEvent: MonitorEvent = {
      id: this.generateEventId(),
      event: "manual_test",
      timestamp: Date.now(),
      data: {
        message: "This is a manual test event",
        timestamp: Date.now(),
      },
    };

    await this.sendEventToServer(testEvent);
  }

  // Method to clear the event queue
  public clearEventQueue(): void {
    const queueLength = this.eventQueue.length;
    this.eventQueue = [];
    console.log(`Event queue cleared. ${queueLength} events were removed.`);
  }

  // Method to get queue status
  public getQueueStatus(): any {
    return {
      queueLength: this.eventQueue.length,
      isProcessing: this.isProcessingUpdate,
      queuedEventTypes: this.eventQueue.map(event => event.event),
      oldestEvent: this.eventQueue.length > 0 ? 
        {
          id: this.eventQueue[0].id,
          event: this.eventQueue[0].event,
          timestamp: this.eventQueue[0].timestamp
        } : null,
      newestEvent: this.eventQueue.length > 0 ? 
        {
          id: this.eventQueue[this.eventQueue.length - 1].id,
          event: this.eventQueue[this.eventQueue.length - 1].event,
          timestamp: this.eventQueue[this.eventQueue.length - 1].timestamp
        } : null
    };
  }

  // Add this to your existing background script

  private async handleContentMessage(
    message: MessageData,
    sender: chrome.runtime.MessageSender
  ): Promise<void> {
    const tabId = sender.tab?.id;
    if (!tabId) return;

    const event: MonitorEvent = {
      id: this.generateEventId(),
      event: "content_message",
      timestamp: Date.now(),
      data: {
        type: message.type,
        tabId,
        url: sender.tab?.url,
        messageData: message.data,
        messageTimestamp: message.timestamp,
      },
    };

    console.log("Message from content script:", event.data);
    await this.sendEventToServer(event);

    switch (message.type) {
      case "DOM_DATA":
        this.updateTabDataWithDOM(tabId, message.data);
        break;
      case "FULL_HTML": // Add this new case
        this.handleFullHTMLData(tabId, message.data);
        break;
      case "VISIBILITY_CHANGE":
        this.logVisibilityChange(tabId, message.data.visibility);
        break;
      case "PAGE_LOADED":
        this.handlePageLoaded(tabId, sender.tab?.url);
        break;
    }
  }

  private async handleFullHTMLData(
    tabId: number,
    htmlData: any
  ): Promise<void> {
    const event: MonitorEvent = {
      id: this.generateEventId(),
      event: "full_html_captured",
      timestamp: Date.now(),
      data: {
        tabId,
        url: htmlData.url,
        title: htmlData.title,
        htmlSize: htmlData.htmlSize,
        fullHTML: htmlData.fullHTML,
        headHTML: htmlData.headHTML,
        bodyHTML: htmlData.bodyHTML,
        documentInfo: htmlData.documentInfo,
        computedStyles: htmlData.computedStyles,
      },
    };

    console.log("Full HTML captured:", {
      tabId,
      url: htmlData.url,
      htmlSize: htmlData.htmlSize,
    });

    await this.sendEventToServer(event);
  }

  // Add method to request full HTML
  private async requestFullHTML(tabId: number): Promise<void> {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          window.dispatchEvent(new CustomEvent("REQUEST_FULL_HTML"));
        },
      });
    } catch (error) {
      console.error("Error requesting full HTML:", error);
    }
  }
}

// Initialize the tab monitor
const tabMonitor = new TabMonitor();

// Make it accessible globally for debugging and configuration
(globalThis as any).tabMonitor = tabMonitor;

// Test server connection on startup
tabMonitor.testServerConnection().then((connected) => {
  console.log(`Server connection: ${connected ? "✅ Connected" : "❌ Failed"}`);
});
