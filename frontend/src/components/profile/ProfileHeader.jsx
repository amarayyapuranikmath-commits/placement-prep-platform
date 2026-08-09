// src/components/profile/ProfileHeader.jsx
import { FiTarget } from 'react-icons/fi'

const getInitials = (name = '') =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || '?'

const ProfileHeader = ({ fullName, targetRole, completionPercentage }) => {
  return (
    <div className="flex flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-accent/15 text-lg font-semibold text-accent">
          {getInitials(fullName)}
        </div>
        <div>
          <h1 className="text-xl font-semibold text-slate-100">{fullName || 'Your Profile'}</h1>
          <div className="mt-1 flex items-center gap-1.5 text-sm text-slate-400">
            <FiTarget size={14} />
            {targetRole ? (
              <span>{targetRole}</span>
            ) : (
              <span className="text-slate-600">No target role set</span>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-2.5">
        <div className="h-1.5 w-28 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-accent transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
        <span className="text-xs font-medium text-slate-300">{completionPercentage}% complete</span>
      </div>
    </div>
  )
}

export default ProfileHeader