import { Outlet, NavLink } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from '../../context/AuthContext'
import { FiHome, FiUser, FiBookOpen, FiFileText, FiTool, FiShield, FiCode, FiBarChart2 } from 'react-icons/fi'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: FiHome },
  { path: '/profile', label: 'Profile', icon: FiUser },
  { path: '/resume', label: 'Resume', icon: FiFileText },
  { path: '/interview', label: 'Interview', icon: FiTool },
  { path: '/aptitude', label: 'Aptitude', icon: FiShield },
  { path: '/coding', label: 'Coding', icon: FiCode },
  { path: '/settings', label: 'Settings', icon: FiBarChart2 },
]

export default function MainLayout() {
  const { user, logout } = useContext(AuthContext)

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <aside className="w-full max-w-[280px] rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
          <div className="space-y-6">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Placement Prep</p>
              <h1 className="mt-3 text-2xl font-semibold text-white">Your study hub</h1>
              <p className="mt-2 text-sm text-slate-400">Build skills, track progress, and practise for interviews.</p>
            </div>

            <div className="rounded-3xl bg-slate-950/80 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Signed in as</p>
              <p className="mt-2 font-semibold text-white">{user?.name || user?.email || 'User'}</p>
            </div>

            <nav className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${
                        isActive ? 'bg-accent text-slate-950' : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                      }`
                    }
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                )
              })}
            </nav>

            <button
              type="button"
              onClick={logout}
              className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm font-medium text-slate-100 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Log out
            </button>
          </div>
        </aside>

        <main className="flex-1 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-glass backdrop-blur-xl">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
