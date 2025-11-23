// Competition Brain Browser Extension - Popup Script

const DEFAULT_SETTINGS = {
  apiUrl: 'http://localhost:3001',
  defaultModels: ['gpt-4o-mini', 'claude-3-5-haiku', 'gemini-1.5-flash'],
  powerLevel: 80,
  timeLimit: 60,
};

let currentSettings = { ...DEFAULT_SETTINGS };

// DOM Elements
const elements = {
  settingsBtn: document.getElementById('settings-btn'),
  settingsPanel: document.getElementById('settings-panel'),
  queryPanel: document.getElementById('query-panel'),
  apiUrlInput: document.getElementById('api-url'),
  defaultModelsInput: document.getElementById('default-models'),
  powerLevelInput: document.getElementById('power-level'),
  powerValue: document.getElementById('power-value'),
  timeLimitInput: document.getElementById('time-limit'),
  timeValue: document.getElementById('time-value'),
  saveSettingsBtn: document.getElementById('save-settings'),
  cancelSettingsBtn: document.getElementById('cancel-settings'),
  queryInput: document.getElementById('query-input'),
  presetSelect: document.getElementById('preset-select'),
  queryBtn: document.getElementById('query-btn'),
  btnText: document.getElementById('btn-text'),
  btnSpinner: document.getElementById('btn-spinner'),
  status: document.getElementById('status'),
  results: document.getElementById('results'),
  resultContent: document.getElementById('result-content'),
  statsModels: document.getElementById('stats-models'),
  statsTime: document.getElementById('stats-time'),
  statsConfidence: document.getElementById('stats-confidence'),
  copyBtn: document.getElementById('copy-btn'),
  expandBtn: document.getElementById('expand-btn'),
  openSidepanelLink: document.getElementById('open-sidepanel'),
};

// Load settings from storage
async function loadSettings() {
  const stored = await chrome.storage.sync.get('settings');

  if (stored.settings) {
    currentSettings = { ...DEFAULT_SETTINGS, ...stored.settings };
  }

  // Update UI
  elements.apiUrlInput.value = currentSettings.apiUrl;
  elements.defaultModelsInput.value = currentSettings.defaultModels.join(', ');
  elements.powerLevelInput.value = currentSettings.powerLevel;
  elements.powerValue.textContent = currentSettings.powerLevel;
  elements.timeLimitInput.value = currentSettings.timeLimit;
  elements.timeValue.textContent = currentSettings.timeLimit;
}

// Save settings to storage
async function saveSettings() {
  currentSettings = {
    apiUrl: elements.apiUrlInput.value,
    defaultModels: elements.defaultModelsInput.value
      .split(',')
      .map(m => m.trim())
      .filter(m => m),
    powerLevel: parseInt(elements.powerLevelInput.value),
    timeLimit: parseInt(elements.timeLimitInput.value),
  };

  await chrome.storage.sync.set({ settings: currentSettings });
  showStatus('Settings saved!', false);
  toggleSettings();
}

// Toggle settings panel
function toggleSettings() {
  const isHidden = elements.settingsPanel.classList.contains('hidden');

  if (isHidden) {
    elements.settingsPanel.classList.remove('hidden');
    elements.queryPanel.classList.add('hidden');
  } else {
    elements.settingsPanel.classList.add('hidden');
    elements.queryPanel.classList.remove('hidden');
  }
}

// Show status message
function showStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.remove('hidden');

  if (isError) {
    elements.status.classList.add('error');
  } else {
    elements.status.classList.remove('error');
  }

  setTimeout(() => {
    elements.status.classList.add('hidden');
  }, 3000);
}

// Get configuration based on preset
function getConfig() {
  const preset = elements.presetSelect.value;

  const configs = {
    fast: {
      models: currentSettings.defaultModels.slice(0, 3),
      powerLevel: 50,
      timeLimit: 30,
    },
    balanced: {
      models: currentSettings.defaultModels,
      powerLevel: 70,
      timeLimit: 60,
    },
    competition: {
      models: ['o1', 'claude-sonnet-4.5', 'gemini-exp-1206', 'gpt-4o', 'deepseek-v3'],
      powerLevel: 95,
      timeLimit: 180,
    },
    free: {
      models: ['gpt-4o-mini', 'claude-3-5-haiku', 'gemini-1.5-flash', 'llama-3.3-70b', 'mistral-small'],
      powerLevel: 70,
      timeLimit: 60,
      freeOnly: true,
    },
    custom: {
      models: currentSettings.defaultModels,
      powerLevel: currentSettings.powerLevel,
      timeLimit: currentSettings.timeLimit,
    },
  };

  return configs[preset] || configs.balanced;
}

// Query Competition Brain API
async function query(text) {
  const config = getConfig();

  // Show loading state
  elements.queryBtn.disabled = true;
  elements.btnText.classList.add('hidden');
  elements.btnSpinner.classList.remove('hidden');
  elements.results.classList.add('hidden');

  try {
    const response = await fetch(`${currentSettings.apiUrl}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: text,
        config: config,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    console.error('Query error:', error);
    showStatus(`Error: ${error.message}`, true);
  } finally {
    // Reset loading state
    elements.queryBtn.disabled = false;
    elements.btnText.classList.remove('hidden');
    elements.btnSpinner.classList.add('hidden');
  }
}

// Display query results
function displayResults(result) {
  elements.resultContent.textContent = result.synthesized;

  const successful = result.individual.filter(r => r.success);
  const avgConfidence = successful.length > 0
    ? (successful.reduce((sum, r) => sum + r.confidence, 0) / successful.length) * 100
    : 0;

  elements.statsModels.textContent = `${successful.length}/${result.individual.length} models`;
  elements.statsTime.textContent = `${result.totalTime.toFixed(2)}s`;
  elements.statsConfidence.textContent = `${avgConfidence.toFixed(0)}% confidence`;

  elements.results.classList.remove('hidden');

  // Store result for side panel
  chrome.storage.local.set({ latestResult: result });
}

// Copy result to clipboard
async function copyResult() {
  const text = elements.resultContent.textContent;

  try {
    await navigator.clipboard.writeText(text);
    showStatus('Copied to clipboard!', false);
  } catch (error) {
    showStatus('Failed to copy', true);
  }
}

// Open side panel
async function openSidePanel() {
  await chrome.sidePanel.open({ windowId: (await chrome.windows.getCurrent()).id });
}

// Event Listeners
elements.settingsBtn.addEventListener('click', toggleSettings);
elements.saveSettingsBtn.addEventListener('click', saveSettings);
elements.cancelSettingsBtn.addEventListener('click', () => {
  loadSettings(); // Reset to saved settings
  toggleSettings();
});

// Update range input displays
elements.powerLevelInput.addEventListener('input', (e) => {
  elements.powerValue.textContent = e.target.value;
});

elements.timeLimitInput.addEventListener('input', (e) => {
  elements.timeValue.textContent = e.target.value;
});

// Query button
elements.queryBtn.addEventListener('click', () => {
  const text = elements.queryInput.value.trim();

  if (!text) {
    showStatus('Please enter a query', true);
    return;
  }

  query(text);
});

// Enter key to submit
elements.queryInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    elements.queryBtn.click();
  }
});

// Copy button
elements.copyBtn.addEventListener('click', copyResult);

// Expand to side panel
elements.expandBtn.addEventListener('click', openSidePanel);

// Open side panel link
elements.openSidepanelLink.addEventListener('click', (e) => {
  e.preventDefault();
  openSidePanel();
});

// Check for selected text from context menu
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'queryText') {
    elements.queryInput.value = message.text;
    query(message.text);
  }
});

// Initialize
loadSettings();
