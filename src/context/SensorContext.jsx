import { createContext, useContext, useState } from 'react'

const SensorContext = createContext({})

export function SensorProvider({ children }) {
  // Placeholder: will hold sensor streams, predictions, robot state in later phases
  const [state, setState] = useState({})

  return (
    <SensorContext.Provider value={{ state, setState }}>
      {children}
    </SensorContext.Provider>
  )
}

export function useSensor() {
  return useContext(SensorContext)
}
