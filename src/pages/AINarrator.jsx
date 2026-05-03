import { useEffect, useRef, useState } from 'react'
import { useSensor } from '../context/SensorContext'
import * as webllm from '@mlc-ai/web-llm'
import { getLatestHeadlines } from '../services/newsEngine'
import { setNarration } from '../utils/devStateStore.js'

function AINarrator() {
  const { fusionActive, fusionResult } = useSensor()
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Initializing AI narrator – loading language model...' }
  ])
  const [isModelReady, setIsModelReady] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const chatEndRef = useRef(null)
  const engineRef = useRef(null)

  // Load WebLLM model on mount
  useEffect(() => {
    const initLLM = async () => {
      try {
        const engine = new webllm.MLCEngine()
        const progressCallback = (report) => {
          // Could update a progress bar here
          console.log('[WebLLM]', report.text)
        }

        // Use Llama-3-8B-Instruct-q4f16_1 (4-bit quantized, ~4GB)
        await engine.reload('Llama-3-8B-Instruct-q4f16_1', { initProgressCallback: progressCallback })

        engineRef.current = engine
        setIsModelReady(true)
        setMessages(prev => [...prev, { role: 'assistant', content: 'AI narrator online. Observing your signals...' }])
      } catch (err) {
        console.error('[WebLLM] load error:', err)
        setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
      }
    }

    initLLM()
    return () => {
      // Cleanup: engine does not have terminate, but we can null it
      engineRef.current = null
    }
  }, [])

  // Auto-generate narration when fusion updates (throttled)
   
  useEffect(() => {
    if (!isModelReady || !fusionActive || !fusionResult || isGenerating) return

    const generateNarration = async () => {
      setIsGenerating(true)

      // Build context from fusion result + news
      const topIntent = Object.entries(fusionResult.intentProbabilities)
        .reduce((a, b) => a[1] > b[1] ? a : b)[0]
      const deceptionP = fusionResult.deceptionProbability

      // Fetch relevant news headlines
      const headlines = await getLatestHeadlines(5)

      const newsContext = headlines.map(h => `• ${h.title}`).join('\n')

      // System prompt
      const systemPrompt = `You are an AI observer integrated into an intention-reading system called IntentScope.
You provide brief, insightful psychological narration based on real-time sensor data.
Be concise (max 2 sentences). Use a sci-fiobserver tone. If deception is indicated, mention it.`

      // User prompt
      let userPrompt = `Current state:
- Top intent: ${topIntent} (confidence: ${Math.round(fusionResult.confidence * 100)}%)
- Deception probability: ${Math.round(deceptionP * 100)}%
- Sensor status: Face: ${Object.keys(fusionResult).length > 0 ? 'active' : 'waiting'}

Latest world news:
${newsContext}

Interpret the user's mental state in one paragraph, considering possible deception and the day's headlines.`

      try {
        const engine = engineRef.current
        if (!engine) throw new Error('Engine not ready')

        // Generate streaming
        const messages = [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ]

        const reply = await engine.chat.completions.create({
          messages,
          stream: true
        })

        let fullText = ''
        // We'll accumulate from streaming chunks
        for await (const chunk of reply) {
          const delta = chunk.choices[0]?.delta?.content || ''
          fullText += delta
          // Update last assistant message progressively
          setMessages(prev => {
            const newMsgs = [...prev]
            const last = newMsgs[newMsgs.length - 1]
            if (last.role === 'assistant') {
              last.content = fullText
            } else {
              newMsgs.push({ role: 'assistant', content: fullText })
            }
            return newMsgs
          })
        }

        setMessages(prev => {
          const newMsgs = [...prev]
          // Ensure final message is set
          if (newMsgs[newMsgs.length - 1].role === 'assistant') {
            newMsgs[newMsgs.length - 1].content = fullText
          } else {
            newMsgs.push({ role: 'assistant', content: fullText })
          }
          return newMsgs
        })
      } catch (err) {
        console.error('[Narrator] generation error:', err)
        setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
      } finally {
        setIsGenerating(false)
      }
    }

    // Debounce: only generate if top intent changed or deception crossed threshold
    generateNarration()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fusionResult?.topIntent, fusionResult?.deceptionProbability])

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Push latest narration to devStateStore (dev-only)
  useEffect(() => {
    if (!import.meta.env.DEV) return
    const latestMsg = messages.filter(m => m.role === 'assistant').pop()
    if (latestMsg) {
      setNarration({
        latestNarration: latestMsg.content,
        lastUpdated: Date.now()
      })
    }
  }, [messages])

  return (
    <div className="container narrator-page">
      <div className="narrator-header">
        <h2>AI Narrator</h2>
        {!isModelReady && (
          <div className="model-status loading">Loading Llama-3-8B (4-bit)... Please wait (5–10 min on first run)</div>
        )}
        {isModelReady && <div className="model-status ready">● Model Ready</div>}
      </div>

      <div className="chat-container card">
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.role === 'user' && <span className="msg-role">You</span>}
              {msg.role === 'system' && <span className="msg-role system">System</span>}
              {msg.role === 'assistant' && <span className="msg-role ai">🎙️ Narrator</span>}
              <p className="msg-content">{msg.content}</p>
            </div>
          ))}
          {isGenerating && (
            <div className="message assistant generating">
              <span className="msg-role ai">🎙️</span>
              <span className="msg-content">
                <span className="typing-indicator">
                  <span>.</span><span>.</span><span>.</span>
                </span>
              </span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            placeholder={isModelReady ? "Ask about your mental state..." : "Loading model..."}
            className="chat-input"
            disabled={!isModelReady || isGenerating}
            onKeyDown={async (e) => {
              if (e.key === 'Enter' && e.target.value.trim() && isModelReady && !isGenerating) {
                const userMsg = e.target.value.trim()
                setMessages(prev => [...prev, { role: 'user', content: userMsg }])
                e.target.value = ''

                // Generate response with WebLLM
                setIsGenerating(true)
                try {
                  const engine = engineRef.current
                  const resp = await engine.chat.completions.create({
                    messages: [...messages, { role: 'user', content: userMsg }],
                    stream: true
                  })
                  let reply = ''
                  for await (const chunk of resp) {
                    reply += chunk.choices[0]?.delta?.content || ''
                    setMessages(prev => {
                      const copy = [...prev]
                      const last = copy[copy.length - 1]
                      if (last.role === 'assistant') {
                        last.content = reply
                      } else {
                        copy.push({ role: 'assistant', content: reply })
                      }
                      return copy
                    })
                  }
                  setMessages(prev => {
                    const copy = [...prev]
                    if (copy[copy.length - 1].role === 'assistant') {
                      copy[copy.length - 1].content = reply
                    } else {
                      copy.push({ role: 'assistant', content: reply })
                    }
                    return copy
                  })
                } catch (err) {
                  setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
                } finally {
                  setIsGenerating(false)
                }
              }
            }}
          />
          <button
            className="btn btn-gold"
            disabled={!isModelReady || isGenerating}
            onClick={() => {/* handled by input onKeyDown */}}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default AINarrator
