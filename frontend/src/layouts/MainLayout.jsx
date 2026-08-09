// src/layouts/MainLayout.jsx
import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from '../components/common/Sidebar'
import Topbar from '../components/common/Topbar'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/dashboard': 'Dashboard',
  '/profile': 'Profile',
  '/resume': 'Resume Analyzer',
  '/coding': 'Coding Practice',
  '/interview': 'AI Interview',
  '/aptitude': 'Aptitude',
  '/roadmap': 'Roadmap',
  '/settings': 'Settings',
  '/ai-insights': 'AI Insights',
}

const MainLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const location = useLocation()

  const pageTitle = PAGE_TITLES[location.pathname] || 'Placement Prep'

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed((prev) => !prev)}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      <div
        className={`flex min-h-screen flex-col transition-all duration-300 ${
          isCollapsed ? 'lg:pl-20' : 'lg:pl-64'
        }`}
      >
        <Topbar onOpenMobile={() => setIsMobileOpen(true)} title={pageTitle} />

        <main className="flex-1 overflow-x-hidden px-3 py-3 sm:px-4 sm:py-4 lg:px-6 lg:py-6 xl:px-8">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default MainLayout