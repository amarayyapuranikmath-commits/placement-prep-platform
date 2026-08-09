import React from 'react'

export default function ConfigurationForm({ values, onChange, onSubmit }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Role</span>
          <input name="role" value={values.role} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none" />
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Company Type</span>
          <input name="companyType" value={values.companyType} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none" />
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Experience Level</span>
          <select name="experience" value={values.experience} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none">
            <option>Junior</option>
            <option>Mid</option>
            <option>Senior</option>
          </select>
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Duration</span>
          <select name="duration" value={values.duration} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none">
            <option>20m</option>
            <option>30m</option>
            <option>40m</option>
          </select>
        </label>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Language</span>
          <select name="language" value={values.language} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none">
            <option>English</option>
            <option>Hindi</option>
            <option>Spanish</option>
          </select>
        </label>
        <label className="space-y-2 text-sm text-slate-300">
          <span className="block font-medium text-slate-100">Voice</span>
          <select name="voice" value={values.voice} onChange={onChange} className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-3 py-2 text-slate-100 outline-none">
            <option>Neutral</option>
            <option>Warm</option>
            <option>Direct</option>
          </select>
        </label>
      </div>

      <div className="flex justify-end">
        <button type="submit" className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-slate-950">Start interview</button>
      </div>
    </form>
  )
}