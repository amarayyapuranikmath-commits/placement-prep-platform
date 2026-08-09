import React from 'react'

export default function ConfigurationForm({ values, options, onChange, onSubmit, submitting }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="space-y-1 text-sm">
          <div className="text-sm font-medium text-slate-100">Role</div>
          <select name="role" value={values.role} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
            {options.roles.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </label>

        <label className="space-y-1 text-sm">
          <div className="text-sm font-medium text-slate-100">Experience</div>
          <select name="experience" value={values.experience} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100">
            {options.experience.map((e) => (
              <option key={e} value={e}>{e}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="flex items-center justify-end">
        <button type="submit" disabled={submitting} className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-accent/90 disabled:opacity-60">Start interview</button>
      </div>
    </form>
  )
}
