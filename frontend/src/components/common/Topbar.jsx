// src/components/common/Topbar.jsx
import { useContext } from 'react'
import { AuthContext } from '../../context/AuthContext'
import { Menu, User } from 'lucide-react'

const getInitials = (fullName, email) => {
  if (fullName) {
    return fullName
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('')
  }
  if (email) {
    return email[0]?.toUpperCase()
  }
  return '?'
}

const Topbar = ({ onOpenMobile, title }) => {
  const { user } = useContext(AuthContext)
  const displayName = user?.full_name || user?.email || 'Account'
  const initials = getInitials(user?.full_name, user?.email)

  return (
    <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-3 border-b border-slate-800 bg-slate-950/80 px-3 backdrop-blur-xl sm:px-4 lg:px-6">
      <button
        type="button"
        onClick={onOpenMobile}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-900 hover:text-slate-100 lg:hidden"
        aria-label="Open navigation"
      >
        <Menu size={19} />
      </button>

      <h1 className="min-w-0 flex-1 truncate text-sm font-semibold text-slate-100 sm:text-base lg:text-lg">
        {title}
      </h1>

      <div className="flex shrink-0 items-center gap-2 sm:gap-3">
        <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/60 py-1 pl-1 pr-2 sm:pr-3">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-xs font-semibold text-accent">
            {initials || <User size={14} />}
          </span>
          <span className="hidden max-w-[120px] truncate text-sm font-medium text-slate-200 sm:inline">
            {displayName}
          </span>
        </div>
      </div>
    </header>
  )
}

export default Topbar