function AINarrator() {
  return (
    <div className="container narrator-page">
      <h2>AI Narrator</h2>

      <div className="chat-container card">
        <div className="chat-messages">
          <div className="message">
            <p className="text-muted">AI is loading local LLM...</p>
          </div>
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            placeholder="Ask about your mental state..."
            className="chat-input"
            disabled
          />
          <button className="btn btn-gold" disabled>Send</button>
        </div>
      </div>
    </div>
  )
}

export default AINarrator
