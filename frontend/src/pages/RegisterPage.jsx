import { useContext, useState } from 'react'
import { Link } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function RegisterPage() {
  const { register } = useContext(AuthContext)
  const [payload, setPayload] = useState({ full_name: '', email: '', password: '' })
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setPayload((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)
    setIsSubmitting(true)

    try {
      await register(payload)
      setSuccess('Registration completed. You can sign in now.')
    } catch (err) {
      const apiErrors = err.response?.data?.errors
      const errorMessage = err.response?.data?.message || err.message || 'Registration failed'

      const validationDetails = Array.isArray(apiErrors)
        ? apiErrors
            .map((errorItem) => {
              if (typeof errorItem === 'string') return errorItem
              const loc = Array.isArray(errorItem.loc) ? errorItem.loc.join('.') : errorItem.loc
              return `${loc ? `${loc}: ` : ''}${errorItem.msg ?? errorItem.message ?? JSON.stringify(errorItem)}`
            })
            .join(' | ')
        : null

      setError(validationDetails ? `${errorMessage} — ${validationDetails}` : errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-950/90 p-8 shadow-glass backdrop-blur-xl">
        <div className="space-y-3 text-center">
          <h1 className="text-3xl font-semibold text-white">Create account</h1>
          <p className="text-sm text-slate-400">Register for the placement prep platform.</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-200">
              Full name
              <input
                type="text"
                name="full_name"
                value={payload.full_name}
                onChange={handleChange}
                required
                className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/30"
              />
            </label>

            <label className="block text-sm font-medium text-slate-200">
              Email address
              <input
                type="email"
                name="email"
                value={payload.email}
                onChange={handleChange}
                required
                className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/30"
              />
            </label>

            <label className="block text-sm font-medium text-slate-200">
              Password
              <input
                type="password"
                name="password"
                value={payload.password}
                onChange={handleChange}
                required
                minLength={8}
                className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-900/90 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/30"
              />
              <p className="mt-2 text-xs text-slate-500">Password must be 8+ chars and include uppercase, lowercase, number, and special character.</p>
            </label>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}
          {success && <p className="text-sm text-emerald-400">{success}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? 'Creating account…' : 'Register'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-white hover:text-accent">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
