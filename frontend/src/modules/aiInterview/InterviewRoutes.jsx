import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import TypeSelection from './pages/TypeSelection'
import Configuration from './pages/Configuration'
import DeviceCheck from './pages/DeviceCheck'
import Live from './pages/Live'
import Report from './pages/Report'
import History from './pages/History'

// Export a self-contained Routes component that can be mounted by the app router.
export default function InterviewRoutes() {
  return (
    <Routes>
      <Route path="/interview" element={<Home />} />
      <Route path="/interview/type" element={<TypeSelection />} />
      <Route path="/interview/configuration" element={<Configuration />} />
      <Route path="/interview/device-check" element={<DeviceCheck />} />
      <Route path="/interview/live" element={<Live />} />
      <Route path="/interview/report" element={<Report />} />
      <Route path="/interview/history" element={<History />} />
      <Route path="/interview/*" element={<Navigate to="/interview" replace />} />
    </Routes>
  )
}
