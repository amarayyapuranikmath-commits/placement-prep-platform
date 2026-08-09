import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="grid min-h-screen place-items-center px-4 py-12 text-center sm:px-6 lg:px-8">
      <div className="max-w-xl rounded-3xl border border-slate-800 bg-slate-950/90 p-10 shadow-glass backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">404</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Page not found</h1>
        <p className="mt-4 text-sm text-slate-400">The page you are looking for does not exist or has moved.</p>
        <Link
          to="/"
          className="mt-8 inline-flex rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-indigo-400"
        >
          Return home
        </Link>
      </div>
    </div>
  )
}
