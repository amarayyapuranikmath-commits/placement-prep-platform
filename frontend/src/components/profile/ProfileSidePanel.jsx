// src/components/profile/ProfileSidePanel.jsx
import { Link } from 'react-router-dom'
import { FiFileText, FiBriefcase, FiCode } from 'react-icons/fi'
import CircularProgress from '../ui/CircularProgress'

const ProfileSidePanel = ({ profile }) => {
  const hasResume = Boolean(profile?.resume_id)
  const skillsCount = profile?.skills?.length || 0
  const targetCompaniesCount = profile?.target_companies?.length || 0

  return (
    <div className="flex flex-col gap-5 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="flex flex-col items-center gap-2 border-b border-slate-800 pb-5">
        <CircularProgress value={profile?.completion_percentage || 0} size="lg" label="Complete" />
      </div>

      <Link
        to="/resume"
        className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 transition-colors hover:border-accent/40"
      >
        <div className="flex items-center gap-2.5">
          <FiFileText size={16} className={hasResume ? 'text-accent' : 'text-slate-500'} />
          <span className="text-sm text-slate-300">Resume</span>
        </div>
        <span
          className={`text-xs font-medium ${hasResume ? 'text-accent' : 'text-slate-500'}`}
        >
          {hasResume ? 'Uploaded' : 'Not uploaded'}
        </span>
      </Link>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-3 text-center">
          <FiCode size={16} className="mx-auto mb-1.5 text-slate-500" />
          <p className="text-lg font-semibold text-slate-100">{skillsCount}</p>
          <p className="text-[11px] text-slate-500">Skills</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-3 text-center">
          <FiBriefcase size={16} className="mx-auto mb-1.5 text-slate-500" />
          <p className="text-lg font-semibold text-slate-100">{targetCompaniesCount}</p>
          <p className="text-[11px] text-slate-500">Target Companies</p>
        </div>
      </div>
    </div>
  )
}

export default ProfileSidePanel