import Dexie from 'dexie'

export const db = new Dexie('IntentScopeDB')

db.version(1).stores({
  models: '++id, name, type, cachedAt, data',
  sessions: '++id, startedAt, endedAt, data'
})

// Initialize and log
db.open().then(() => {
  console.log('[DB] IndexedDB ready')
}).catch(err => {
  console.error('[DB] Failed to open:', err)
})

export default db
