const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

/**
 * Response Cache with TTL and optional persistence
 */
class ResponseCache {
  constructor(options = {}) {
    this.cache = new Map();
    this.ttl = options.ttl || 3600000; // 1 hour default
    this.maxSize = options.maxSize || 1000;
    this.persistPath = options.persistPath || path.join(__dirname, '../../.cache');
    this.enabled = options.enabled !== false;

    if (this.enabled && options.persist) {
      this.loadFromDisk();
    }
  }

  /**
   * Generate cache key from query and config
   */
  generateKey(query, config) {
    const normalized = {
      query: query.toLowerCase().trim(),
      models: config.models.sort(),
      powerLevel: config.powerLevel,
      // Don't include timeLimit in key (not affecting response quality)
    };
    return crypto.createHash('sha256').update(JSON.stringify(normalized)).digest('hex');
  }

  /**
   * Get cached response
   */
  get(query, config) {
    if (!this.enabled) return null;

    const key = this.generateKey(query, config);
    const cached = this.cache.get(key);

    if (!cached) return null;

    // Check TTL
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    console.log(`[Cache] HIT for query: "${query.slice(0, 50)}..."`);
    cached.hits++;
    return cached.data;
  }

  /**
   * Set cached response
   */
  set(query, config, data) {
    if (!this.enabled) return;

    const key = this.generateKey(query, config);

    // Enforce max size (LRU - remove oldest)
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      hits: 0,
      query: query.slice(0, 100), // Store first 100 chars for debugging
    });

    console.log(`[Cache] SET for query: "${query.slice(0, 50)}..."`);
  }

  /**
   * Clear all cache
   */
  clear() {
    this.cache.clear();
    console.log('[Cache] Cleared');
  }

  /**
   * Get cache statistics
   */
  stats() {
    const entries = Array.from(this.cache.values());
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      ttl: this.ttl,
      enabled: this.enabled,
      totalHits: entries.reduce((sum, e) => sum + e.hits, 0),
      oldestEntry: entries.length > 0 ?
        new Date(Math.min(...entries.map(e => e.timestamp))) : null,
    };
  }

  /**
   * Save cache to disk
   */
  saveToDisk() {
    if (!this.enabled) return;

    const data = {
      version: 1,
      timestamp: Date.now(),
      entries: Array.from(this.cache.entries()).map(([key, value]) => ({
        key,
        ...value,
      })),
    };

    try {
      if (!fs.existsSync(this.persistPath)) {
        fs.mkdirSync(this.persistPath, { recursive: true });
      }
      fs.writeFileSync(
        path.join(this.persistPath, 'responses.json'),
        JSON.stringify(data, null, 2)
      );
      console.log('[Cache] Saved to disk');
    } catch (error) {
      console.error('[Cache] Save error:', error.message);
    }
  }

  /**
   * Load cache from disk
   */
  loadFromDisk() {
    if (!this.enabled) return;

    try {
      const cachePath = path.join(this.persistPath, 'responses.json');
      if (!fs.existsSync(cachePath)) return;

      const data = JSON.parse(fs.readFileSync(cachePath, 'utf8'));

      // Only load non-expired entries
      const now = Date.now();
      data.entries.forEach(entry => {
        if (now - entry.timestamp < this.ttl) {
          const { key, ...value } = entry;
          this.cache.set(key, value);
        }
      });

      console.log(`[Cache] Loaded ${this.cache.size} entries from disk`);
    } catch (error) {
      console.error('[Cache] Load error:', error.message);
    }
  }

  /**
   * Export cache for analysis
   */
  export() {
    return Array.from(this.cache.entries()).map(([key, value]) => ({
      key,
      query: value.query,
      hits: value.hits,
      age: Date.now() - value.timestamp,
      models: value.data.individual.map(i => i.model),
    }));
  }
}

// Global cache instance
let cacheInstance = null;

/**
 * Get or create cache instance
 */
function getCache(options) {
  if (!cacheInstance) {
    cacheInstance = new ResponseCache(options);
  }
  return cacheInstance;
}

module.exports = { ResponseCache, getCache };
