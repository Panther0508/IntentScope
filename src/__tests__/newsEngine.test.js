import { describe, it, expect, beforeEach, vi } from 'vitest'
import { db } from '../db'
import { refreshNews, getLatestHeadlines, clearCache, getCacheSize } from '../services/newsEngine'

describe('News Engine', () => {
  beforeEach(async () => {
    // Clear DB before each test
    await clearCache()
  })

  it('should start with empty cache', async () => {
    const count = await db.news.count()
    expect(count).toBe(0)
  })

  it('should fetch and cache articles', async () => {
    // Refresh will hit real APIs; mock fetch to avoid rate limits
    global.fetch = vi.fn(async (url) => {
      if (url.includes('hn.algolia.com')) {
        return {
          ok: true,
          json: async () => ({
            hits: [{ objectID: '1', title: 'Test HN', created_at: 1700000000, story_text: null }]
          })
        }
      }
      if (url.includes('dev.to')) {
        return {
          ok: true,
          json: async () => ([{ title: 'Dev.to article', url: 'https://dev.to/test', description: 'desc', published_at: '2024-01-01T00:00:00Z' }])
        }
      }
      if (url.includes('reddit')) {
        return {
          ok: true,
          json: async () => ({
            data: { children: [{ data: { title: 'Reddit post', selftext: 'body', created_utc: 1700000000, url: 'https://reddit.com/r/test', permalink: '/r/test' } }] }
          })
        }
      }
      return { ok: false }
    })

    const articles = await refreshNews()
    expect(articles.length).toBeGreaterThan(0)
  })

  it('should get latest headlines sorted by timestamp', async () => {
    // Insert test data
    await db.news.bulkAdd([
      { title: 'Old', timestamp: new Date(1000), source: 'HN', url: '', snippet: '', keywords: [] },
      { title: 'New', timestamp: new Date(9999999999), source: 'HN', url: '', snippet: '', keywords: [] }
    ])
    const latest = await getLatestHeadlines(2)
    expect(latest[0].title).toBe('New')
  })

  it('should clear cache', async () => {
    await db.news.bulkAdd([{ title: 'A', timestamp: new Date(), source: 'HN', url: '', snippet: '', keywords: [] }])
    await clearCache()
    const count = await db.news.count()
    expect(count).toBe(0)
  })

  it('should report cache size', async () => {
    await db.news.bulkAdd([
      { title: 'A', timestamp: new Date(), source: 'HN', url: '', snippet: '', keywords: [] }
    ])
    const size = await getCacheSize()
    expect(size).toMatch(/B|KB|MB/)
  })
})
