import { useEffect, useState } from 'react'
import { getLatestHeadlines } from '../services/newsEngine'

function NewsTicker() {
  const [articles, setArticles] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)

  useEffect(() => {
    // Load initial articles
    getLatestHeadlines(5).then(setArticles)

    // Refresh every 5 minutes (matched with engine's interval)
    const interval = setInterval(() => {
      getLatestHeadlines(5).then(setArticles)
    }, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [])

  // Rotate every 5 seconds
  useEffect(() => {
    if (articles.length === 0) return
    const timer = setInterval(() => {
      setCurrentIdx((i) => (i + 1) % articles.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [articles.length])

  if (articles.length === 0) return null

  const article = articles[currentIdx]

  // Truncate title
  const maxLen = 60
  const displayTitle = article.title.length > maxLen
    ? article.title.substring(0, maxLen) + '…'
    : article.title

  return (
    <div className="news-ticker glass">
      <span className="news-source">{article.source}</span>
      <span className="news-title">{displayTitle}</span>
      <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">→</a>
    </div>
  )
}

export default NewsTicker
