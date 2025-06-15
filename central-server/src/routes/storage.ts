import { Router, Request, Response } from 'express';
import { StorageItem, StorageResponse, StorageStats, ErrorResponse } from '../types';

class StorageService {
  private storage: Map<string, StorageItem> = new Map();

  public set(key: string, data: string): StorageResponse {
    try {
      const item: StorageItem = {
        key,
        data,
        timestamp: Date.now(),
        size: Buffer.byteLength(data, 'utf8')
      };

      this.storage.set(key, item);

      return {
        success: true,
        message: `Data stored successfully for key: ${key}`,
        timestamp: item.timestamp
      };
    } catch (error) {
      throw new Error(`Failed to store data: ${error}`);
    }
  }

  public get(key: string): StorageResponse {
    const item = this.storage.get(key);

    if (!item) {
      return {
        success: false,
        message: `No data found for key: ${key}`
      };
    }

    try {
      // Try to parse as JSON, if it fails return as string
      let parsedData;
      try {
        parsedData = JSON.parse(item.data);
      } catch {
        parsedData = item.data;
      }

      return {
        success: true,
        data: parsedData,
        timestamp: item.timestamp
      };
    } catch (error) {
      throw new Error(`Failed to retrieve data: ${error}`);
    }
  }

  public delete(key: string): StorageResponse {
    const existed = this.storage.delete(key);

    return {
      success: true,
      message: existed
        ? `Data deleted successfully for key: ${key}`
        : `No data found for key: ${key}`
    };
  }

  public getStats(): StorageStats {
    const keys = Array.from(this.storage.keys());
    const totalSize = Array.from(this.storage.values())
      .reduce((sum, item) => sum + item.size, 0);

    return {
      totalKeys: keys.length,
      totalSize,
      keys
    };
  }

  public clear(): StorageResponse {
    const keyCount = this.storage.size;
    this.storage.clear();

    return {
      success: true,
      message: `Cleared ${keyCount} keys from storage`
    };
  }

  public exists(key: string): boolean {
    return this.storage.has(key);
  }
}

const storageService = new StorageService();
const router = Router();

// Middleware for request logging
// router.use((req: Request, res: Response, next) => {
//   console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`, 
//     req.method === 'POST' ? { body: req.body } : { query: req.query });
//   next();
// });

// POST /api/storage/:key - Store data
router.post('/:key', (req: Request, res: Response) => {
  try {
    const { key } = req.params;
    const { data } = req.body;

    if (!key) {
      const error: ErrorResponse = {
        success: false,
        error: 'Key is required',
        timestamp: Date.now()
      };
      return res.status(400).json(error);
    }

    if (data === undefined || data === null) {
      const error: ErrorResponse = {
        success: false,
        error: 'Data is required',
        timestamp: Date.now()
      };
      return res.status(400).json(error);
    }

    // Convert data to string if it's not already
    const stringData = typeof data === 'string' ? data : JSON.stringify(data);

    const result = storageService.set(key, stringData);
    res.status(201).json(result);
  } catch (error) {
    const errorResponse: ErrorResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: Date.now()
    };
    res.status(500).json(errorResponse);
  }
});

// GET /api/storage/:key - Retrieve data
router.get('/:key', (req: Request, res: Response) => {
  try {
    const { key } = req.params;

    if (!key) {
      const error: ErrorResponse = {
        success: false,
        error: 'Key is required',
        timestamp: Date.now()
      };
      return res.status(400).json(error);
    }

    const result = storageService.get(key);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    const errorResponse: ErrorResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: Date.now()
    };
    res.status(500).json(errorResponse);
  }
});

// DELETE /api/storage/:key - Delete data
router.delete('/:key', (req: Request, res: Response) => {
  try {
    const { key } = req.params;

    if (!key) {
      const error: ErrorResponse = {
        success: false,
        error: 'Key is required',
        timestamp: Date.now()
      };
      return res.status(400).json(error);
    }

    const result = storageService.delete(key);
    res.json(result);
  } catch (error) {
    const errorResponse: ErrorResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: Date.now()
    };
    res.status(500).json(errorResponse);
  }
});

// GET /api/storage - Get storage stats
router.get('/', (req: Request, res: Response) => {
  try {
    const stats = storageService.getStats();
    res.json({
      success: true,
      data: stats,
      timestamp: Date.now()
    });
  } catch (error) {
    const errorResponse: ErrorResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: Date.now()
    };
    res.status(500).json(errorResponse);
  }
});

// DELETE /api/storage - Clear all data
router.delete('/', (req: Request, res: Response) => {
  try {
    const result = storageService.clear();
    res.json(result);
  } catch (error) {
    const errorResponse: ErrorResponse = {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      timestamp: Date.now()
    };
    res.status(500).json(errorResponse);
  }
});

// HEAD /api/storage/:key - Check if key exists
router.head('/:key', (req: Request, res: Response) => {
  try {
    const { key } = req.params;
    const exists = storageService.exists(key);
    res.status(exists ? 200 : 404).end();
  } catch (error) {
    res.status(500).end();
  }
});

export default router;