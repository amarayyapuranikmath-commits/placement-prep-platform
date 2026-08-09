import { AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import AppRoutes from './routes/AppRoutes'

function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AnimatePresence mode="wait" initial={false}>
        <AppRoutes location={location} />
      </AnimatePresence>
    </div>
  )
}

export default App
