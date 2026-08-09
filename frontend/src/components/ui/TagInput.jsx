// src/components/ui/TagInput.jsx
import { useState } from 'react'
import { FiX } from 'react-icons/fi'

const TagInput = ({ value = [], onChange, placeholder = 'Type and press Enter' }) => {
  const [draft, setDraft] = useState('')

  const addTag = (raw) => {
    const cleaned = raw.trim()
    if (!cleaned) return
    const exists = value.some((tag) => tag.toLowerCase() === cleaned.toLowerCase())
    if (!exists) {
      onChange([...value, cleaned])
    }
    setDraft('')
  }

  const removeTag = (index) => {
    onChange(value.filter((_, i) => i !== index))
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addTag(draft)
    } else if (event.key === 'Backspace' && draft === '' && value.length > 0) {
      removeTag(value.length - 1)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-800 bg-slate-950/60 px-3 py-2.5 focus-within:border-accent/60">
      {value.map((tag, index) => (
        <span
          key={`${tag}-${index}`}
          className="flex items-center gap-1.5 rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent"
        >
          {tag}
          <button
            type="button"
            onClick={() => removeTag(index)}
            className="text-accent/70 transition-colors hover:text-accent"
            aria-label={`Remove ${tag}`}
          >
            <FiX size={12} />
          </button>
        </span>
      ))}
      <input
        type="text"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={() => addTag(draft)}
        placeholder={value.length === 0 ? placeholder : ''}
        className="min-w-[120px] flex-1 bg-transparent text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none"
      />
    </div>
  )
}

export default TagInput