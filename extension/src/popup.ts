document.addEventListener('DOMContentLoaded', async () => {
  const serverUrlInput = document.getElementById('serverUrl') as HTMLInputElement;
  const enabledCheckbox = document.getElementById('enabled') as HTMLInputElement;
  const saveButton = document.getElementById('saveConfig') as HTMLButtonElement;
  const testButton = document.getElementById('testConnection') as HTMLButtonElement;
  const retryButton = document.getElementById('retryFailed') as HTMLButtonElement;
  const statusDiv = document.getElementById('status') as HTMLDivElement;

  // Load current configuration
  const result = await chrome.storage.sync.get(['serverConfig']);
  const config = result.serverConfig || {
    baseUrl: 'http://localhost:3000/api/storage',
    enabled: true
  };

  serverUrlInput.value = config.baseUrl;
  enabledCheckbox.checked = config.enabled;

  // Save configuration
  saveButton.addEventListener('click', async () => {
    const newConfig = {
      baseUrl: serverUrlInput.value,
      enabled: enabledCheckbox.checked,
      retryAttempts: 3,
      retryDelay: 1000
    };

    await chrome.storage.sync.set({ serverConfig: newConfig });
    
    // Update background script
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.runtime.sendMessage({
      type: 'UPDATE_CONFIG',
      config: newConfig
    });

    showStatus('Configuration saved successfully!', 'success');
  });

  // Test connection
  testButton.addEventListener('click', async () => {
    try {
      const healthUrl = serverUrlInput.value.replace('/api/storage', '') + '/health';
      const response = await fetch(healthUrl);
      const result = await response.json();
      
      if (response.ok) {
        showStatus('✅ Server connection successful!', 'success');
      } else {
        showStatus('❌ Server connection failed', 'error');
      }
    } catch (error) {
      showStatus('❌ Server connection failed: ' + error, 'error');
    }
  });

  // Retry failed requests
  retryButton.addEventListener('click', async () => {
    chrome.runtime.sendMessage({ type: 'RETRY_FAILED_REQUESTS' });
    showStatus('Retrying failed requests...', 'success');
  });

  function showStatus(message: string, type: 'success' | 'error') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    setTimeout(() => {
      statusDiv.textContent = '';
      statusDiv.className = '';
    }, 3000);
  }
});