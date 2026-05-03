import Dexie from 'dexie'

export const db = new Dexie('IntentScopeDB')

// Version 2: adds news table
db.version(2).stores({
  models: '++id, name, type, cachedAt, data',
  sessions: '++id, startedAt, endedAt, data',
  news: '++id, title, url, source, snippet, timestamp, keywords'  // World Knowledge Engine cache
})

// Initialize and log
db.open().then(() => {
  console.log('[DB] IndexedDB ready')
}).catch(err => {
  console.error('[DB] Failed to open:', err)
})

export default db
