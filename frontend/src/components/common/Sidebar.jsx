// src/components/common/Sidebar.jsx
import { useContext } from 'react'
import { NavLink } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import {
  LayoutDashboard,
  FileText,
  Code2,
  MessageSquare,
  Brain,
  BarChart3,
  Sparkles,
  Map,
  User,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  X,
} from 'lucide-react'

const NAV_SECTIONS = [
  {
    heading: 'GENERAL',
    items: [{ path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }],
  },
  {
    heading: 'PREPARATION',
    items: [
      { path: '/resume', label: 'Resume Analyzer', icon: FileText },
      { path: '/coding', label: 'Coding Practice', icon: Code2 },
      { path: '/interview', label: 'AI Interview', icon: MessageSquare },
      { path: '/aptitude', label: 'Aptitude', icon: Brain },
    ],
  },
  {
    heading: 'ANALYTICS',
    items: [
      { path: '/progress', label: 'Progress', icon: BarChart3 },
      { path: '/ai-insights', label: 'AI Insights', icon: Sparkles },
    ],
  },
  {
    heading: 'ACCOUNT',
    items: [
      { path: '/profile', label: 'Profile', icon: User },
      { path: '/settings', label: 'Settings', icon: Settings },
    ],
  },
]

const Sidebar = ({ isCollapsed, onToggleCollapse, isMobileOpen, onCloseMobile }) => {
  const { logout } = useContext(AuthContext)
  const isDesktopViewport = typeof window !== 'undefined' && window.innerWidth >= 1024
  const isSidebarVisible = isDesktopViewport || isMobileOpen
  const sidebarTransform = isSidebarVisible ? 'translateX(0%)' : 'translateX(-100%)'

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-950/60 lg:hidden"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      <aside
        style={{ transform: sidebarTransform, display: isSidebarVisible ? 'flex' : 'none' }}
        className={`fixed inset-y-0 left-0 z-40 flex h-screen w-72 flex-col border-r border-slate-800 bg-slate-950 shadow-2xl shadow-slate-950/50 transition-all duration-300 ${
          isCollapsed ? 'lg:w-20' : 'lg:w-64'
        }`}
      >
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 px-4">
          <div
            className={`flex items-center gap-2 overflow-hidden ${
              isCollapsed ? 'lg:w-0 lg:opacity-0' : ''
            } transition-all duration-300`}
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent/15 text-accent">
              <GraduationCap size={18} />
            </span>
            <span
              className={`whitespace-nowrap text-sm font-semibold text-slate-100 ${
                isCollapsed ? 'lg:hidden' : ''
              }`}
            >
              Placement Prep
            </span>
          </div>

          <button
            type="button"
            onClick={onToggleCollapse}
            className="hidden h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-800 hover:text-slate-200 lg:flex"
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>

          <button
            type="button"
            onClick={onCloseMobile}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-800 hover:text-slate-200 lg:hidden"
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {NAV_SECTIONS.map(({ heading, items }) => (
            <div key={heading} className="mt-5 first:mt-0">
              <p
                className={`mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-600 ${
                  isCollapsed ? 'lg:hidden' : ''
                }`}
              >
                {heading}
              </p>
              <div
                className={`mx-3 mb-2 hidden h-px bg-slate-800 ${isCollapsed ? 'lg:block' : ''}`}
              />

              <div className="space-y-1">
                {items.map(({ path, label, icon: Icon, comingSoon }) =>
                  comingSoon ? (
                    <div
                      key={path}
                      title={isCollapsed ? `${label} (coming soon)` : undefined}
                      className={`flex cursor-not-allowed items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 ${
                        isCollapsed ? 'lg:justify-center' : ''
                      }`}
                    >
                      <Icon size={18} className="shrink-0" />
                      <span
                        className={`flex flex-1 items-center justify-between truncate ${
                          isCollapsed ? 'lg:hidden' : ''
                        }`}
                      >
                        {label}
                        <span className="ml-2 shrink-0 rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-500">
                          Soon
                        </span>
                      </span>
                    </div>
                  ) : (
                    <NavLink
                      key={path}
                      to={path}
                      onClick={onCloseMobile}
                      title={isCollapsed ? label : undefined}
                      className={({ isActive }) =>
                        `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                          isActive
                            ? 'bg-accent/15 text-accent'
                            : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100'
                        } ${isCollapsed ? 'lg:justify-center' : ''}`
                      }
                    >
                      <Icon size={18} className="shrink-0" />
                      <span className={`truncate ${isCollapsed ? 'lg:hidden' : ''}`}>
                        {label}
                      </span>
                    </NavLink>
                  )
                )}
              </div>
            </div>
          ))}
        </nav>

        <div className="shrink-0 border-t border-slate-800 p-3">
          <button
            type="button"
            onClick={logout}
            title={isCollapsed ? 'Logout' : undefined}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-red-500/10 hover:text-red-400 ${
              isCollapsed ? 'lg:justify-center' : ''
            }`}
          >
            <LogOut size={18} className="shrink-0" />
            <span className={isCollapsed ? 'lg:hidden' : ''}>Logout</span>
          </button>
        </div>
      </aside>
    </>
  )
}

export default Sidebar