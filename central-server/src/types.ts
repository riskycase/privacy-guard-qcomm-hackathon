export interface StorageItem {
  key: string;
  data: string;
  timestamp: number;
  size: number;
}

export interface StorageResponse {
  success: boolean;
  message?: string;
  data?: any;
  timestamp?: number;
}

export interface StorageStats {
  totalKeys: number;
  totalSize: number;
  keys: string[];
}

export interface ErrorResponse {
  success: false;
  error: string;
  timestamp: number;
}