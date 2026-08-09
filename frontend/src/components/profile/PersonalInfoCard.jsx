// src/components/profile/PersonalInfoCard.jsx
import { FiUser } from 'react-icons/fi'

const PersonalInfoCard = ({ fullName, email, phone, onChange }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <FiUser size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-slate-100">Personal Information</h2>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Full Name</label>
          <input
            type="text"
            value={fullName || ''}
            disabled
            className="w-full cursor-not-allowed rounded-2xl border border-slate-800 bg-slate-950/40 px-3 py-2.5 text-sm text-slate-500"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Email</label>
          <input
            type="email"
            value={email || ''}
            disabled
            className="w-full cursor-not-allowed rounded-2xl border border-slate-800 bg-slate-950/40 px-3 py-2.5 text-sm text-slate-500"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Phone Number</label>
          <input
            type="tel"
            value={phone || ''}
            onChange={(event) => onChange('phone', event.target.value)}
            placeholder="+1 234 567 8900"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>
      </div>
    </div>
  )
}

export default PersonalInfoCard