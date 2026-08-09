import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from '../components/common/ProtectedRoute'
import MainLayout from '../layouts/MainLayout'
import PageLoader from '../components/ui/PageLoader'

const LandingPage = lazy(() => import('../pages/LandingPage'))
const LoginPage = lazy(() => import('../pages/LoginPage'))
const RegisterPage = lazy(() => import('../pages/RegisterPage'))
const DashboardPage = lazy(() => import('../pages/DashboardPage'))
const ProfilePage = lazy(() => import('../pages/ProfilePage'))
const RoadmapPage = lazy(() => import('../pages/RoadmapPage'))
const ResumePage = lazy(() => import('../pages/ResumePage'))
const InterviewPage = lazy(() => import('../pages/InterviewPage'))
const AptitudePage = lazy(() => import('../pages/AptitudePage'))
const CodingPage = lazy(() => import('../pages/CodingPage'))
const CodingProblemPage = lazy(() => import('../pages/CodingProblemPage'))
const SettingsPage = lazy(() => import('../pages/SettingsPage'))
const ProgressPage = lazy(() => import('../pages/ProgressPage'))
const AIInsightsPage = lazy(() => import('../pages/AIInsightsPage'))
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'))

const RouteShell = ({ children }) => (
  <Suspense fallback={<PageLoader label="Loading page..." />}>{children}</Suspense>
)

function AppRoutes({ location }) {
  return (
    <Routes location={location} key={location.pathname}>
      <Route path="/" element={<RouteShell><LandingPage /></RouteShell>} />
      <Route path="/login" element={<RouteShell><LoginPage /></RouteShell>} />
      <Route path="/register" element={<RouteShell><RegisterPage /></RouteShell>} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><DashboardPage /></RouteShell>} />
      </Route>

      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><ProfilePage /></RouteShell>} />
      </Route>

      <Route
        path="/roadmap"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><RoadmapPage /></RouteShell>} />
      </Route>

      <Route
        path="/resume"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><ResumePage /></RouteShell>} />
      </Route>

      <Route
        path="/interview"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><InterviewPage /></RouteShell>} />
      </Route>

      <Route
        path="/aptitude"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><AptitudePage /></RouteShell>} />
      </Route>

      <Route
        path="/coding"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><CodingPage /></RouteShell>} />
        <Route path=":problemId" element={<RouteShell><CodingProblemPage /></RouteShell>} />
      </Route>

      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><SettingsPage /></RouteShell>} />
      </Route>

      <Route
        path="/progress"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><ProgressPage /></RouteShell>} />
      </Route>

      <Route
        path="/ai-insights"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<RouteShell><AIInsightsPage /></RouteShell>} />
      </Route>

      <Route path="*" element={<RouteShell><NotFoundPage /></RouteShell>} />
    </Routes>
  )
}

export default AppRoutes   