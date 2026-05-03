export default function Tutorial() {
  return (
    <div className="container tutorial-page">
      <h2>Interactive Tutorial</h2>
      <p className="text-muted">A step-by-step walkthrough of IntentScope&apos;s features and how to use them effectively.</p>

      <div className="card">
        <h3>Step 1 – Introduction</h3>
        <p>IntentScope combines face tracking, voice stress analysis, and keyboard dynamics into a unified intention prediction engine.</p>

        <h4>Key Concepts:</h4>
        <ul>
          <li><strong>Gaze Tracking:</strong> Where are you looking? Eye direction is a strong signal of interest or intention.</li>
          <li><strong>Action Units (AUs):</strong> Micro-expressions detected from facial landmarks hint at emotional states.</li>
          <li><strong>Voice Stress:</strong> Pitch jitter, shimmer, and MFCC patterns correlate with cognitive load or deception.</li>
          <li><strong>Keyboard Dynamics:</strong> Typing rhythm reveals hesitation or confidence.</li>
        </ul>

        <div className="tutorial-nav">
          <button className="btn btn-primary" disabled>Start Tutorial Walkthrough</button>
        </div>
      </div>

      <div className="card">
        <h3>Step 2 – Dashboard Overview</h3>
        <p>The Dashboard shows live sensor panels:</p>
        <ul>
          <li><strong>Gaze Overlay:</strong> Webcam view with gaze vector drawn</li>
          <li><strong>Deception Gauge:</strong> Real-time probability that you&apos;re being deceptive</li>
          <li><strong>Intent Bars:</strong> 8-class probability distribution</li>
          <li><strong>News Ticker:</strong> World headlines relevant to your current intention</li>
        </ul>
      </div>

      <div className="card">
        <h3>Step 3 – Try It Yourself</h3>
        <p>1. Click <strong>&quot;Start Sensors&quot;</strong> and allow camera/mic permissions.</p>
        <p>2. Look at different parts of the screen; notice how &quot;Exploring&quot; goes up when your gaze jumps between items.</p>
        <p>3. Speak – try varying your pitch and loudness; see how voice stress affects the &quot;Hesitation&quot; or &quot;BuyIntent&quot; classes.</p>
        <p>4. Type in any text field (if available) and watch the keyboard stats fill.</p>
      </div>

      <div className="card">
        <h3>Step 4 – Deception Challenge</h3>
        <p>Navigate to the <strong>Deception</strong> page. You&apos;ll answer personal yes/no questions. Try answering truthfully vs. lying and observe the deception gauge spike when you&apos;re insincere.</p>
      </div>

      <div className="card">
        <h3>Step 5 – Robot Lab</h3>
        <p>Switch to <strong>Robot Lab</strong>. When your &quot;RobotPick&quot; intent crosses ~85% threshold, the simulated arm will reach for an object. Try to will the arm to move with your mind!</p>
      </div>

      <div className="card">
        <h3>Step 6 – Advanced Features</h3>
        <ul>
          <li><strong>Narrator:</strong> Ask the AI &quot;What am I thinking?&quot; and it will comment on your mental state, including recent news context.</li>
          <li><strong>Playground:</strong> Replay recorded sessions without a camera. Great for testing or demos offline.</li>
          <li><strong>API Gateway:</strong> During development, <code>curl http://localhost:3000/api/intent</code> returns live JSON predictions.</li>
          <li><strong>Diagnostics:</strong> Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd> for an overlay with performance metrics.</li>
        </ul>
      </div>

      <div className="card">
        <h3>Step 7 – Training Your Own Model</h3>
        <p>The included training pipeline lets you retrain the fusion model with new data.</p>
        <pre>{`cd training
python generate_dataset.py   # create synthetic data
python train_fusion_model.py # train Bi-LSTM & export ONNX
# copy public/fusion_model.onnx and restart app`}</pre>
      </div>

      <div className="tutorial-nav">
        <button className="btn btn-outline" disabled>Previous</button>
        <button className="btn btn-primary" disabled>Next</button>
      </div>
    </div>
  )
}
