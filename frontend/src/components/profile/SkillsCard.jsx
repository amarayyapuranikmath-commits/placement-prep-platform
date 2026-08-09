// src/components/profile/SkillsCard.jsx
import { FiCode } from 'react-icons/fi'
import TagInput from '../ui/TagInput'

const SkillsCard = ({ skills, onChange }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
      <div className="mb-5 flex items-center gap-2">
        <FiCode size={16} className="text-accent" />
        <h2 className="text-sm font-semibold text-slate-100">Skills</h2>
      </div>

      <TagInput
        value={skills || []}
        onChange={(next) => onChange('skills', next)}
        placeholder="e.g. Python, press Enter"
      />
    </div>
  )
}

export default SkillsCard