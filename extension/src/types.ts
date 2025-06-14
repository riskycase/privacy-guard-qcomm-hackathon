export interface TabData {
  url: string;
  title: string;
  tabId: number;
  timestamp: number;
  screenshot?: string;
  domData?: DOMData;
  visibility: 'visible' | 'hidden';
}

export interface DOMData {
  title: string;
  url: string;
  domain: string;
  elementCount: number;
  imageCount: number;
  linkCount: number;
  textContent: string;
  metaTags: Record<string, string>;
}

export interface MessageData {
  type: 'DOM_DATA' | 'VISIBILITY_CHANGE' | 'PAGE_LOADED';
  data: any;
  tabId: number;
  timestamp: number;
}