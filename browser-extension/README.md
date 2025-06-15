# Tab Monitor Extension

A Chrome extension that monitors tab changes, captures page data, and sends events to a central server.

## Features

- Monitors tab activation, updates, and visibility changes
- Configurable server connection settings
- Retry mechanism for failed server communications

## Installation

### Development Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd privacy-guard-qcomm-hackathon/browser-extension
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the extension:
   ```
   npm run build
   ```

4. Load the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `dist` directory from this project

### Production Installation

Once published to the Chrome Web Store:
1. Visit the Chrome Web Store page for Tab Monitor Extension
2. Click "Add to Chrome"
3. Follow the prompts to install the extension

## Usage

After installation, the extension will automatically start monitoring your tabs and sending data to the configured server.

### Extension Popup

Click on the extension icon in your browser toolbar to:
- View current monitoring status
- Configure server settings
- Test server connection

### Server Configuration

By default, the extension connects to a local server at `http://localhost:3000/api/storage`. You can change this in the extension popup.

## Development

### Project Structure

- `src/background.ts`: Background service worker that handles tab monitoring and server communication
- `src/content.ts`: Content script that extracts URL
- `src/popup.html` & `src/popup.ts`: Extension popup UI
- `src/types.ts`: TypeScript type definitions

### Available Scripts

- `npm run dev`: Build in development mode with watch mode enabled
- `npm run build`: Build for production
- `npm run clean`: Remove build artifacts

## Building for Production

To build the extension for production:

```
npm run build
```

This will create a `dist` directory with the compiled extension files.

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

