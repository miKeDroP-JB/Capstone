// Competition Brain Browser Extension - Side Panel Script

const DEFAULT_SETTINGS = {
  apiUrl: 'http://localhost:3001',
  defaultModels: ['gpt-4o-mini', 'claude-3-5-haiku', 'gemini-1.5-flash'],
  powerLevel: 80,
  timeLimit: 60,
};

let currentSettings = { ...DEFAULT_SETTINGS };

// DOM Elements
const elements = {
  queryInput: document.getElementById('query-input'),
  presetSelect: document.getElementById('preset-select'),
  queryBtn: document.getElementById('query-btn'),
  btnText: document.getElementById('btn-text'),
  btnSpinner: document.getElementById('btn-spinner'),
  status: document.getElementById('status'),
  noResults: document.getElementById('no-results'),
  results: document.getElementById('results'),
  synthesizedContent: document.getElementById('synthesized-content'),
  statModels: document.getElementById('stat-models'),
  statTime: document.getElementById('stat-time'),
  statConfidence: document.getElementById('stat-confidence'),
  individualList: document.getElementById('individual-list'),
  copyBtn: document.getElementById('copy-btn'),
};

// Load settings
async function loadSettings() {
  const stored = await chrome.storage.sync.get('settings');

  if (stored.settings) {
    currentSettings = { ...DEFAULT_SETTINGS, ...stored.settings };
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
  }, 4000);
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
      models: ['gpt-4o-mini', 'claude-3-5-haiku', 'gemini-1.5-flash', 'llama-3.3-70b'],
      powerLevel: 70,
      timeLimit: 60,
      freeOnly: true,
    },
  };

  return configs[preset] || configs.balanced;
}

// Query API
async function query(text) {
  const config = getConfig();

  // Show loading state
  elements.queryBtn.disabled = true;
  elements.btnText.classList.add('hidden');
  elements.btnSpinner.classList.remove('hidden');

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

    // Store result
    chrome.storage.local.set({ latestResult: result });
  } catch (error) {
    console.error('Query error:', error);
    showStatus(`Error: ${error.message}. Make sure the backend is running.`, true);
  } finally {
    // Reset loading state
    elements.queryBtn.disabled = false;
    elements.btnText.classList.remove('hidden');
    elements.btnSpinner.classList.add('hidden');
  }
}

// Display results
function displayResults(result) {
  // Hide empty state
  elements.noResults.classList.add('hidden');
  elements.results.classList.remove('hidden');

  // Synthesized response
  elements.synthesizedContent.textContent = result.synthesized;

  // Calculate stats
  const successful = result.individual.filter(r => r.success);
  const avgConfidence = successful.length > 0
    ? (successful.reduce((sum, r) => sum + r.confidence, 0) / successful.length) * 100
    : 0;

  elements.statModels.textContent = `${successful.length}/${result.individual.length}`;
  elements.statTime.textContent = `${result.totalTime.toFixed(1)}s`;
  elements.statConfidence.textContent = `${avgConfidence.toFixed(0)}%`;

  // Individual responses
  elements.individualList.innerHTML = '';

  result.individual.forEach((item) => {
    const div = document.createElement('div');
    div.className = 'individual-item';

    const header = document.createElement('div');
    header.className = 'individual-header';

    const modelName = document.createElement('div');
    modelName.className = 'model-name';
    modelName.textContent = item.model;

    const meta = document.createElement('div');
    meta.className = 'individual-meta';

    const statusBadge = document.createElement('span');
    statusBadge.className = `badge ${item.success ? 'badge-success' : 'badge-error'}`;
    statusBadge.textContent = item.success ? '✓ Success' : '✗ Failed';

    const confidence = document.createElement('span');
    confidence.textContent = `${(item.confidence * 100).toFixed(0)}% confidence`;

    const time = document.createElement('span');
    time.textContent = `${item.time.toFixed(2)}s`;

    meta.appendChild(statusBadge);
    meta.appendChild(confidence);
    meta.appendChild(time);

    header.appendChild(modelName);
    header.appendChild(meta);

    const content = document.createElement('div');
    content.className = 'individual-content';
    content.textContent = item.response;

    div.appendChild(header);
    div.appendChild(content);

    elements.individualList.appendChild(div);
  });

  // Scroll to top
  document.getElementById('results-container').scrollTop = 0;
}

// Copy result
async function copyResult() {
  const text = elements.synthesizedContent.textContent;

  try {
    await navigator.clipboard.writeText(text);
    showStatus('Copied to clipboard!', false);
  } catch (error) {
    showStatus('Failed to copy', true);
  }
}

// Event Listeners
elements.queryBtn.addEventListener('click', () => {
  const text = elements.queryInput.value.trim();

  if (!text) {
    showStatus('Please enter a query', true);
    return;
  }

  query(text);
});

elements.queryInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    elements.queryBtn.click();
  }
});

elements.copyBtn.addEventListener('click', copyResult);

// Listen for messages (from context menu or popup)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'queryText') {
    elements.queryInput.value = message.text;
    query(message.text);
  }
});

// Load latest result if available
async function loadLatestResult() {
  const stored = await chrome.storage.local.get('latestResult');

  if (stored.latestResult) {
    displayResults(stored.latestResult);
  }
}

// Initialize
loadSettings();
loadLatestResult();
