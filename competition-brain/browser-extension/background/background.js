// Competition Brain Browser Extension - Background Service Worker

// Create context menu on installation
chrome.runtime.onInstalled.addListener(() => {
  // Context menu for selected text
  chrome.contextMenus.create({
    id: 'query-selected-text',
    title: 'Query with Competition Brain',
    contexts: ['selection'],
  });

  // Context menu to open side panel
  chrome.contextMenus.create({
    id: 'open-sidepanel',
    title: 'Open Competition Brain Side Panel',
    contexts: ['page', 'action'],
  });

  console.log('Competition Brain extension installed');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'query-selected-text') {
    // Send selected text to popup
    const selectedText = info.selectionText;

    // Try to open popup and send message
    chrome.action.openPopup().then(() => {
      // Wait a bit for popup to load
      setTimeout(() => {
        chrome.runtime.sendMessage({
          action: 'queryText',
          text: selectedText,
        });
      }, 100);
    }).catch(() => {
      // If popup fails, try side panel
      chrome.sidePanel.open({ windowId: tab.windowId }).then(() => {
        chrome.runtime.sendMessage({
          action: 'queryText',
          text: selectedText,
        });
      });
    });
  } else if (info.menuItemId === 'open-sidepanel') {
    chrome.sidePanel.open({ windowId: tab.windowId });
  }
});

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
  if (command === 'open_sidepanel') {
    chrome.windows.getCurrent((window) => {
      chrome.sidePanel.open({ windowId: window.id });
    });
  }
});

// Handle messages from popup/sidepanel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'openSidePanel') {
    chrome.windows.getCurrent((window) => {
      chrome.sidePanel.open({ windowId: window.id });
      sendResponse({ success: true });
    });
    return true; // Keep channel open for async response
  }
});

console.log('Competition Brain background service worker loaded');
