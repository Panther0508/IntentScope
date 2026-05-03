import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import './additional.css'
import { SensorProvider } from './context/SensorContext.jsx'
import './db' // Initialize IndexedDB

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <SensorProvider>
        <App />
      </SensorProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
