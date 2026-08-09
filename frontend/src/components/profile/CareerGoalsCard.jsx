// src/components/profile/CareerGoalsCard.jsx
import { FiFlag } from 'react-icons/fi'
import TagInput from '../ui/TagInput'

const CareerGoalsCard = ({ targetRole, targetCompanies, onChange }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <FiFlag size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-slate-100">Career Goals</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Target Role</label>
          <input
            type="text"
            value={targetRole || ''}
            onChange={(event) => onChange('target_role', event.target.value)}
            placeholder="e.g. Software Development Engineer"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Target Companies</label>
          <TagInput
            value={targetCompanies || []}
            onChange={(next) => onChange('target_companies', next)}
            placeholder="e.g. Google, press Enter"
          />
        </div>
      </div>
    </div>
  )
}

export default CareerGoalsCard