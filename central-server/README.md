# Express Key-Value Storage Server

A simple Express.js server that provides key-value storage functionality for the Tab Monitor Extension.

## Features

- RESTful API for storing and retrieving data
- In-memory key-value storage
- CORS support for cross-origin requests
- Compression for reduced bandwidth usage
- Security headers with Helmet
- Health check endpoint

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/` | API documentation |
| POST | `/api/storage/:key` | Store data with the specified key |
| GET | `/api/storage/:key` | Retrieve data by key |
| DELETE | `/api/storage/:key` | Delete data by key |
| HEAD | `/api/storage/:key` | Check if key exists |
| GET | `/api/storage` | Get storage statistics |
| DELETE | `/api/storage` | Clear all data |

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd privacy-guard-qcomm-hackathon/central-server
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the server:
   ```
   npm run build
   ```

4. Start the server:
   ```
   npm start
   ```

## Usage

### Starting the Server

For development with hot-reloading:
```
npm run dev
```

For production:
```
npm run build
npm start
```

By default, the server runs on port 3000. You can change this by setting the `PORT` environment variable.

### API Usage Examples

#### Store Data
```bash
curl -X POST http://localhost:3000/api/storage/mykey \
  -H "Content-Type: application/json" \
  -d '{"data": {"message": "Hello, world!"}}'
```

#### Retrieve Data
```bash
curl http://localhost:3000/api/storage/mykey
```

#### Delete Data
```bash
curl -X DELETE http://localhost:3000/api/storage/mykey
```

#### Get Storage Statistics
```bash
curl http://localhost:3000/api/storage
```

#### Clear All Data
```bash
curl -X DELETE http://localhost:3000/api/storage
```

#### Health Check
```bash
curl http://localhost:3000/health
```

## Development

### Project Structure

- `src/server.ts`: Main server file with Express configuration
- `src/routes/storage.ts`: Storage API routes and in-memory storage implementation
- `src/types.ts`: TypeScript type definitions

### Available Scripts

- `npm run dev`: Start the server in development mode with hot-reloading
- `npm run build`: Build for production
- `npm start`: Start the production server
- `npm run clean`: Remove build artifacts

### Environment Variables

- `PORT`: The port to run the server on (default: 3000)
- `CORS_ORIGIN`: CORS origin setting (default: '*')

## Integration with Tab Monitor Extension

This server is designed to work with the Tab Monitor Extension. The extension sends events to this server, which stores them for later retrieval and analysis.

To use with the extension:
1. Start this server
2. Configure the extension to point to this server (default: http://localhost:3000/api/storage)

## License

MIT License

Copyright (c) 2025 Hrishikesh Patil

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

