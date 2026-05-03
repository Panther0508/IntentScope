/**
 * World Knowledge Engine – Real-time News Caching & Retrieval
 * ===========================================================
 * Fetches headlines from Hacker News, Dev.to, and Reddit r/programming.
 * Caches them in IndexedDB via Dexie for offline access.
 * Provides keyword-based relevance matching for narrator context.
 */

import { db } from '../db'

// Article table schema
const ARTICLES_STORE = 'news'

// Ensure table exists
db.version(1).stores({
  news: '++id, title, url, source, snippet, timestamp, keywords'
})

const SOURCES = {
  HACKER_NEWS: 'HN',
  DEV_TO: 'Dev.to',
  REDDIT: 'Reddit'
}

/**
 * Fetch Hacker News top stories (Algolia API)
 * https://hn.algolia.com/api
 */
async function fetchHackerNews() {
  try {
    const resp = await fetch('https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=10')
    const data = await resp.json()
    const articles = data.hits.map(hit => ({
      title: hit.title || '',
      url: hit.url || `https://news.ycombinator.com/item?id=${hit.objectID}`,
      source: SOURCES.HACKER_NEWS,
      snippet: hit.story_text ? hit.story_text.substring(0, 200) : '',
      timestamp: new Date(hit.created_at * 1000),
      keywords: extractKeywords(hit.title + ' ' + (hit.story_text || ''))
    }))
    return articles
  } catch (err) {
    console.error('[NewsEngine] HN fetch failed:', err)
    return []
  }
}

/**
 * Fetch latest articles from Dev.to
 * https://docs.dev.to/api/
 */
async function fetchDevTo() {
  try {
    const resp = await fetch('https://dev.to/api/articles?per_page=10')
    const data = await resp.json()
    const articles = data.map(article => ({
      title: article.title || '',
      url: article.url || '',
      source: SOURCES.DEV_TO,
      snippet: article.description ? article.description.substring(0, 200) : '',
      timestamp: new Date(article.published_at),
      keywords: extractKeywords(article.title + ' ' + (article.description || ''))
    }))
    return articles
  } catch (err) {
    console.error('[NewsEngine] Dev.to fetch failed:', err)
    return []
  }
}

/**
 * Fetch top posts from r/programming
 * Reddit JSON API with custom User-Agent
 */
async function fetchRedditProgramming() {
  try {
    const resp = await fetch('https://www.reddit.com/r/programming/.json?limit=10', {
      headers: {
        'User-Agent': 'IntentScope/1.0 (by Panther0508)'
      }
    })
    const data = await resp.json()
    const articles = (data.data?.children || []).map(post => {
      const p = post.data
      return {
        title: p.title || '',
        url: p.url ? (p.url.startsWith('http') ? p.url : `https://reddit.com${p.permalink}`) : '',
        source: SOURCES.REDDIT,
        snippet: (p.selftext || '').substring(0, 200),
        timestamp: new Date(p.created_utc * 1000),
        keywords: extractKeywords(p.title + ' ' + (p.selftext || ''))
      }
    })
    return articles
  } catch (err) {
    console.error('[NewsEngine] Reddit fetch failed:', err)
    return []
  }
}

/**
 * Very simple keyword extractor – lowercase, split, remove stopwords
 */
function extractKeywords(text) {
  if (!text) return []
  const stopwords = new Set(['the','and','for','with','that','this','but','are','was','have','has','had','not','from','into','over','under','between','after','before','when','while','because','since','each','any','some','such','only','own','just','than','then','too','very','can','will','just','should','now','out','up','down','off','again','further','here','there','where','why','how','all','both','few','more','most','other','such','no','nor','too','very','s','t','don','now'])
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3 && !stopwords.has(word))
    .slice(0, 5)  // up to 5 keywords per article
}

/**
 * Core function: fetch from all sources, clear old, store fresh
 */
export async function refreshNews() {
  console.log('[NewsEngine] Refreshing news from all sources...')
  const start = performance.now()

  // Fetch concurrently
  const [hn, dev, reddit] = await Promise.all([
    fetchHackerNews(),
    fetchDevTo(),
    fetchRedditProgramming()
  ])

  const all = [...hn, ...dev, ...reddit]

  // Clear existing and bulk-add
  try {
    await db.news.clear()
    await db.news.bulkAdd(all)
    console.log(`[NewsEngine] ✓ Refreshed ${all.length} articles in ${(performance.now() - start).toFixed(1)}ms`)
  } catch (err) {
    console.error('[NewsEngine] DB write error:', err)
  }

  return all
}

/**
 * Get latest headlines (most recent by timestamp)
 */
export function getLatestHeadlines(count = 5) {
  return db.news
    .orderBy('timestamp')
    .reverse()
    .limit(count)
    .toArray()
}

/**
 * Get headlines relevant to a query string (keyword matching over title+snippet+keywords)
 */
export async function getRelevantHeadlines(query, count = 5) {
  if (!query || typeof query !== 'string') {
    return getLatestHeadlines(count)
  }

  const qwords = query.toLowerCase().split(/\s+/).filter(w => w.length > 3)

  const all = await db.news.toArray()
  if (all.length === 0) return []

  // Score each article by keyword overlap
  const scored = all.map(article => {
    const text = (article.title + ' ' + article.snippet + ' ' + article.keywords.join(' ')).toLowerCase()
    let score = 0
    for (const w of qwords) {
      if (text.includes(w)) score += 1
    }
    return { article, score }
  }).filter(item => item.score > 0)

  scored.sort((a, b) => b.score - a.score)
  return scored.slice(0, count).map(item => item.article)
}

/**
 * Start periodic refresh (every 5 minutes)
 */
let refreshIntervalId = null
export function startPeriodicRefresh(intervalMs = 5 * 60 * 1000) {
  // Initial fetch
  refreshNews().catch(console.error)

  refreshIntervalId = setInterval(() => {
    refreshNews().catch(console.error)
  }, intervalMs)

  console.log(`[NewsEngine] Periodic refresh started (${intervalMs / 60000} min)`)
}

export function stopPeriodicRefresh() {
  if (refreshIntervalId) {
    clearInterval(refreshIntervalId)
    refreshIntervalId = null
    console.log('[NewsEngine] Periodic refresh stopped')
  }
}

/**
 * Intelligent query builder from sensor state
 */
export function buildNewsQuery(sensorState) {
  // sensorState: { intentProbabilities, deceptionProbability, faceData, voiceData }
  const { intentProbabilities, deceptionProbability } = sensorState

  if (!intentProbabilities) return ''

  // Find top intent
  const topIntent = Object.entries(intentProbabilities).reduce((a, b) => a[1] > b[1] ? a : b)[0]

  // Map intent to search keywords
  const intentKeywords = {
    Exploring: 'discovery exploration technology research',
    BuyIntent: 'shopping deals e-commerce consumer tech',
    Hesitation: 'decision making productivity focus',
    Deception: 'trust psychology lie detection ethics security',
    ActionConfirm: 'workflow automation efficiency',
    RobotPick: 'robotics automation grasping AI control',
    RobotPlace: 'robotics manipulation spatial reasoning',
    RobotIdle: 'standby monitoring idle systems'
  }

  let query = intentKeywords[topIntent] || ''

  // If deception > 0.3, add trust-related boost
  if (deceptionProbability > 0.3) {
    query += ' trust security authentication'
  }

  return query.trim()
}

// Convenience: entry-getLatestHeadlines for immediate use
export async function getNewsDigest(count = 5) {
  const latest = await getLatestHeadlines(count)
  if (latest.length === 0) {
    // Trigger a fetch in background if empty
    refreshNews()
  }
  return latest
}
