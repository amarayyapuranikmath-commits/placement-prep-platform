AI Interview module (isolated)

Overview
- This folder contains a fully isolated AI Interview module. It does not modify any shared components or routes.

How to integrate
1. Import and mount the routes in your existing app router (for example, in `frontend/src/routes/AppRoutes.jsx`):

   import InterviewRoutes from '../modules/aiInterview/InterviewRoutes'

   // Then include inside your top-level <Routes>:
   <Route path="/*" element={<AppLayout />}>
     ...existing routes...
     {/* Mount isolated interview routes */}
     <Route path="/interview/*" element={<InterviewRoutes />} />
   </Route>

2. Alternatively, you can import specific pages and link to them directly using links like `/interview`, `/interview/type`.

Notes
- No existing files were modified by this module.
- All styles use existing Tailwind classes and the app's design tokens (e.g. `bg-accent`, `border-slate-800`).
- If you want me to mount these routes into `AppRoutes.jsx` for you, I can do that after your approval (I will explain the single, minimal change first).
