# Competition Brain Browser Extension

Access Competition Brain's multi-agent AI orchestration from anywhere in your browser.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Chrome](https://img.shields.io/badge/Chrome-Compatible-brightgreen)
![Edge](https://img.shields.io/badge/Edge-Compatible-brightgreen)

---

## Features

- 🚀 **Quick Access** - Popup interface with keyboard shortcut (Ctrl/Cmd+Shift+B)
- 🖱️ **Context Menu** - Right-click selected text to query instantly
- 📌 **Side Panel** - Full interface for detailed results (Ctrl/Cmd+Shift+S)
- ⚙️ **Customizable** - Configure API URL, models, and power settings
- 💾 **Persistent Settings** - Your preferences sync across devices
- 📋 **Copy Results** - One-click copy to clipboard
- 🎯 **Presets** - Fast, Balanced, Competition, and Free modes

---

## Installation

### Option 1: Load Unpacked (Development)

1. **Open Chrome/Edge Extensions**
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`

2. **Enable Developer Mode**
   - Toggle "Developer mode" in top-right corner

3. **Load Extension**
   - Click "Load unpacked"
   - Select the `browser-extension` directory
   - Extension should appear in your toolbar

4. **Add Icons** (Optional)
   - Add icon files to `icons/` directory (see `icons/README.md`)
   - Reload extension

### Option 2: Chrome Web Store (Future)

_Coming soon after testing and refinement_

---

## Setup

### 1. Configure Backend URL

First time setup:

1. Click the extension icon 🧠
2. Click the settings icon ⚙️
3. Enter your backend URL:
   - Local: `http://localhost:3001`
   - Railway: `https://your-app.railway.app`
   - Vercel/Other: `https://your-backend-url.com`
4. Click "Save"

### 2. Test Connection

1. Enter a test query: "What is 2+2?"
2. Click "Query"
3. You should see a response within a few seconds

If it fails:
- Verify backend is running
- Check console for errors (F12 → Console tab)
- Ensure CORS is enabled in backend

---

## Usage

### Quick Query (Popup)

1. **Click extension icon** 🧠 (or press `Ctrl/Cmd+Shift+B`)
2. **Enter your question**
3. **Select preset** (Fast, Balanced, Competition, Free)
4. **Click "Query"**
5. **View synthesized result**

**Tips**:
- Press `Enter` while typing to submit
- Shift+Enter for new line
- Click 📋 to copy result
- Click ↗️ to expand to side panel

### Context Menu (Selected Text)

1. **Select text** on any web page
2. **Right-click** → "Query with Competition Brain"
3. Extension popup opens with selected text
4. **Auto-queries** the selected text
5. View result in popup or side panel

**Use Cases**:
- Define unfamiliar terms
- Explain code snippets
- Get multiple perspectives on quotes
- Analyze article excerpts

### Side Panel (Full View)

1. **Click extension icon** → "Open Side Panel"
   - Or press `Ctrl/Cmd+Shift+S`
   - Or right-click → "Open Competition Brain Side Panel"

2. **Enter query** in larger text area
3. **View detailed results**:
   - Synthesized response
   - Statistics (models, time, confidence)
   - Individual agent responses
   - Model-specific insights

**When to Use**:
- Complex queries needing detailed analysis
- Comparing individual model responses
- Working alongside research/writing
- Extended sessions with multiple queries

---

## Configuration

### Settings

Access via popup → ⚙️ icon:

- **Backend URL**: Your Competition Brain API endpoint
- **Default Models**: Comma-separated model IDs
- **Power Level**: 0-100% (quality vs speed)
- **Time Limit**: 5-300 seconds per query

**Recommended Settings**:

**Development**:
```
Backend URL: http://localhost:3001
Models: gpt-4o-mini, gemini-1.5-flash
Power: 50%
Time: 30s
```

**Production**:
```
Backend URL: https://your-backend.railway.app
Models: gpt-4o, claude-sonnet-4.5, gemini-exp-1206
Power: 80%
Time: 60s
```

### Presets

**Fast** (3 models, 30s, 50% power)
- Best for: Quick answers, simple queries
- Cost: ~$0.01 per query
- Time: 5-10 seconds

**Balanced** (default models, 60s, 70% power)
- Best for: General use, daily queries
- Cost: ~$0.05 per query
- Time: 10-20 seconds

**Competition** (top 5 models, 180s, 95% power)
- Best for: High-stakes decisions, complex problems
- Cost: ~$0.50-2.00 per query
- Time: 30-60 seconds

**Free** (free models only, 60s, 70% power)
- Best for: High-volume use, testing
- Cost: $0 (with rate limits)
- Time: 10-30 seconds

---

## Keyboard Shortcuts

- `Ctrl/Cmd+Shift+B` - Open popup
- `Ctrl/Cmd+Shift+S` - Open side panel
- `Enter` (in popup) - Submit query
- `Shift+Enter` (in popup) - New line
- `Ctrl/Cmd+Enter` (in side panel) - Submit query

**Customize**:
1. Go to `chrome://extensions/shortcuts`
2. Find "Competition Brain"
3. Click pencil icon to change shortcuts

---

## Permissions

The extension requires:

- **storage** - Save your settings and preferences
- **contextMenus** - Add right-click menu options
- **sidePanel** - Enable side panel feature
- **host_permissions** - Connect to your backend API
  - `http://localhost:3001/*` - Local development
  - `https://*.railway.app/*` - Railway hosting
  - `https://*.vercel.app/*` - Vercel hosting

**Privacy**:
- No data is collected or sent to third parties
- All queries go directly to YOUR backend
- Settings stored locally in browser
- Open source - audit the code yourself

---

## Troubleshooting

### "Connection refused" or "Network error"

**Problem**: Can't reach backend

**Solutions**:
1. Verify backend is running:
   ```bash
   curl http://localhost:3001/health
   ```
2. Check backend URL in settings
3. Ensure no firewall blocking requests
4. Check browser console (F12) for CORS errors

### "All models failed"

**Problem**: Backend responded but all models errored

**Solutions**:
1. Check backend logs for errors
2. Verify API keys are configured in backend
3. Test backend directly:
   ```bash
   curl -X POST http://localhost:3001/api/query \
     -H "Content-Type: application/json" \
     -d '{"query":"test","config":{"models":["gpt-4o-mini"],"powerLevel":50}}'
   ```

### Context menu not appearing

**Problem**: Right-click menu doesn't show extension option

**Solutions**:
1. Reload extension (chrome://extensions → reload)
2. Check extension is enabled
3. Try selecting text again
4. Restart browser

### Side panel not opening

**Problem**: Side panel command doesn't work

**Solutions**:
1. Ensure you're on Chrome 114+ or Edge 114+
2. Update browser to latest version
3. Use popup instead (always works)

### Settings not saving

**Problem**: Changes to settings don't persist

**Solutions**:
1. Check "storage" permission is granted
2. Clear extension storage and try again
3. Reinstall extension

---

## Development

### Project Structure

```
browser-extension/
├── manifest.json           # Extension configuration
├── popup/
│   ├── popup.html          # Popup interface
│   ├── popup.css           # Popup styles
│   └── popup.js            # Popup logic
├── sidepanel/
│   ├── sidepanel.html      # Side panel interface
│   ├── sidepanel.css       # Side panel styles
│   └── sidepanel.js        # Side panel logic
├── background/
│   └── background.js       # Service worker (context menu, etc.)
└── icons/
    ├── icon16.png
    ├── icon32.png
    ├── icon48.png
    └── icon128.png
```

### Making Changes

1. **Edit files** (popup.js, etc.)
2. **Reload extension**:
   - Go to `chrome://extensions`
   - Click reload icon on Competition Brain
3. **Test changes** by using extension

### Adding Features

**Example**: Add new preset

1. **Edit `popup/popup.js`** and `sidepanel/sidepanel.js`
2. Add to `configs` object:
   ```javascript
   custom: {
     models: ['your-models'],
     powerLevel: 90,
     timeLimit: 120,
   }
   ```
3. **Edit HTML** to add option:
   ```html
   <option value="custom">Custom</option>
   ```
4. Reload extension and test

### Testing

**Manual Testing**:
1. Load extension in Chrome
2. Test all features:
   - Popup query
   - Context menu
   - Side panel
   - Settings save/load
   - Copy to clipboard
3. Check console for errors

**API Testing**:
```javascript
// In browser console while extension open
chrome.storage.sync.get('settings', (data) => {
  console.log('Settings:', data.settings);
});
```

---

## Publishing to Chrome Web Store

When ready to publish:

1. **Create icons** (all 4 sizes)
2. **Test thoroughly** on multiple sites
3. **Create screenshots** for store listing
4. **Write description** (see manifest.json)
5. **Zip extension**:
   ```bash
   cd browser-extension
   zip -r competition-brain-extension.zip . -x "*.git*" -x "README.md"
   ```
6. **Upload** to https://chrome.google.com/webstore/devconsole
7. **Fill out listing**:
   - Name: Competition Brain
   - Category: Productivity
   - Language: English
   - Privacy policy: Link to your policy
8. **Submit for review** (takes 1-3 days)

**Cost**: $5 one-time developer registration fee

---

## Roadmap

- [ ] Firefox support (WebExtensions)
- [ ] Safari support (Safari Web Extension)
- [ ] Offline mode (cache responses)
- [ ] Query history
- [ ] Export results (PDF, Markdown)
- [ ] Streaming responses
- [ ] Model comparison view
- [ ] Custom themes
- [ ] Keyboard-only navigation

---

## Support

**Issues**: https://github.com/miKeDroP-JB/Capstone/issues

**Documentation**:
- [Main README](../README.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [SDK Documentation](../sdk/README.md)

---

## License

MIT - See [LICENSE](../LICENSE) file

---

**Enjoy multi-agent AI from anywhere! 🧠✨**
