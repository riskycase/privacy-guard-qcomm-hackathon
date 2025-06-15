# Privacy Guard - Tab Monitoring System

A comprehensive browser monitoring system consisting of a Chrome extension and a central server for capturing and storing browsing data.

## Project Components

This project consists of two main components:

1. **Tab Monitor Extension**: A Chrome extension that monitors tab activity, captures screenshots, DOM data, and HTML content.
2. **Central Server**: An Express.js server that provides key-value storage for the data captured by the extension.

## Architecture Overview

```
┌─────────────────────┐      HTTP/JSON       ┌─────────────────────┐
│                     │  ----------------->  │                     │
│   Tab Monitor       │                      │   Central Server    │
│   Extension         │  <-----------------  │   (Express.js)      │
│                     │      Responses       │                     │
└─────────────────────┘                      └─────────────────────┘
        |                                             |
        | Monitors                                    | Stores
        ↓                                             ↓
   Browser Activity                              In-memory Storage
   - Tab changes                                 - Latest URL
```

## Features

- Real-time tab activity monitoring
- RESTful API for data storage and retrieval
- In-memory key-value storage

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- Chromium based browser (for extension)

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd privacy-guard-qcomm-hackathon
   ```

2. Set up the central server:
   ```
   cd central-server
   npm install
   npm run build
   npm start
   ```

3. Set up the extension:
   ```
   cd ../extension
   npm install
   npm run build
   ```

4. Load the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `dist` directory from the extension folder

## Usage

1. Start the central server:
   ```
   cd central-server
   npm start
   ```

2. The extension will automatically start monitoring tabs and sending data to the server once installed.

3. Access the stored data through the central server's API endpoints.

## Development

Each component has its own development workflow. Please refer to the README.md files in the respective directories for detailed development instructions:

- [Tab Monitor Extension](./browser-extension/README.md)
- [Central Server](./central-server/README.md)

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

## Acknowledgments

- [List any acknowledgments, libraries, or tools used]
