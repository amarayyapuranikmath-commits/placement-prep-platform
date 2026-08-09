// src/components/profile/ProfessionalLinksCard.jsx
import { FiGithub, FiLinkedin } from 'react-icons/fi'

const ProfessionalLinksCard = ({ githubUrl, linkedinUrl, onChange }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <FiGithub size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-slate-100">Professional Links</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-slate-500">
            <FiGithub size={12} /> GitHub URL
          </label>
          <input
            type="url"
            value={githubUrl || ''}
            onChange={(event) => onChange('github_url', event.target.value)}
            placeholder="https://github.com/yourusername"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-slate-500">
            <FiLinkedin size={12} /> LinkedIn URL
          </label>
          <input
            type="url"
            value={linkedinUrl || ''}
            onChange={(event) => onChange('linkedin_url', event.target.value)}
            placeholder="https://linkedin.com/in/yourusername"
            className="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 text-sm text-slate-200 placeholder:text-slate-600 focus:border-accent/60 focus:outline-none"
          />
        </div>
      </div>
    </div>
  )
}

export default ProfessionalLinksCard