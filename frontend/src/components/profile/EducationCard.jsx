// src/components/profile/EducationCard.jsx
import { FiBookOpen } from 'react-icons/fi'

const EducationCard = ({ college, degree, branch, graduationYear, cgpa, onChange }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <FiBookOpen size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-slate-100">Education</h2>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="mb-1.5 block text-xs font-medium text-slate-500">College / University</label>
          <input
            type="text"
            value={college || ''}
            onChange={(event) => onChange('college', event.target.value)}
            placeholder="e.g. Indian Institute of Technology"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Degree</label>
          <input
            type="text"
            value={degree || ''}
            onChange={(event) => onChange('degree', event.target.value)}
            placeholder="e.g. B.Tech"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Branch</label>
          <input
            type="text"
            value={branch || ''}
            onChange={(event) => onChange('branch', event.target.value)}
            placeholder="e.g. Computer Science"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">Graduation Year</label>
          <input
            type="number"
            min={2000}
            max={2100}
            value={graduationYear ?? ''}
            onChange={(event) =>
              onChange('graduation_year', event.target.value ? Number(event.target.value) : null)
            }
            placeholder="2026"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-slate-500">CGPA</label>
          <input
            type="number"
            min={0}
            max={10}
            step={0.01}
            value={cgpa ?? ''}
            onChange={(event) =>
              onChange('cgpa', event.target.value ? Number(event.target.value) : null)
            }
            placeholder="8.5"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>
      </div>
    </div>
  )
}

export default EducationCard