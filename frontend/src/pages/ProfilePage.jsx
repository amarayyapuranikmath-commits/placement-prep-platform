import { useContext, useEffect, useState } from 'react'
import { AuthContext } from '../context/AuthContext'
import { useProfile } from '../hooks/useProfile'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import SuccessBanner from '../components/ui/SuccessBanner'
import ProfileHeader from '../components/profile/ProfileHeader'
import ProfileSidePanel from '../components/profile/ProfileSidePanel'
import PersonalInfoCard from '../components/profile/PersonalInfoCard'
import EducationCard from '../components/profile/EducationCard'
import SkillsCard from '../components/profile/SkillsCard'
import CareerGoalsCard from '../components/profile/CareerGoalsCard'
import ProfessionalLinksCard from '../components/profile/ProfessionalLinksCard'

const buildInitialFormData = (profile, user) => ({
  phone: profile?.phone ?? '',
  college: profile?.college ?? '',
  degree: profile?.degree ?? '',
  branch: profile?.branch ?? '',
  graduation_year: profile?.graduation_year ?? null,
  cgpa: profile?.cgpa ?? null,
  target_role: profile?.target_role ?? '',
  target_companies: profile?.target_companies ?? [],
  skills: profile?.skills ?? [],
  github_url: profile?.github_url ?? '',
  linkedin_url: profile?.linkedin_url ?? '',
  full_name: user?.full_name ?? user?.email ?? '',
})

export default function ProfilePage() {
  const { user } = useContext(AuthContext)
  const { profile, isLoading, error, isSaving, saveProfile, refetch } = useProfile()
  const [formData, setFormData] = useState(() => buildInitialFormData(profile, user))
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    setFormData(buildInitialFormData(profile, user))
  }, [profile, user])

  const handleFieldChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    const payload = {
      phone: formData.phone?.trim() ? formData.phone.trim() : null,
      college: formData.college?.trim() ? formData.college.trim() : null,
      degree: formData.degree?.trim() ? formData.degree.trim() : null,
      branch: formData.branch?.trim() ? formData.branch.trim() : null,
      graduation_year: formData.graduation_year ?? null,
      cgpa: formData.cgpa ?? null,
      target_role: formData.target_role?.trim() ? formData.target_role.trim() : null,
      target_companies: formData.target_companies ?? [],
      skills: formData.skills ?? [],
      github_url: formData.github_url?.trim() ? formData.github_url.trim() : null,
      linkedin_url: formData.linkedin_url?.trim() ? formData.linkedin_url.trim() : null,
    }

    try {
      await saveProfile(payload)
      setSuccessMessage('Profile saved successfully')
    } catch {
      setSuccessMessage('')
    }
  }

  const displayProfile = profile
    ? {
        ...profile,
        phone: formData.phone || null,
        college: formData.college || null,
        degree: formData.degree || null,
        branch: formData.branch || null,
        graduation_year: formData.graduation_year ?? null,
        cgpa: formData.cgpa ?? null,
        target_role: formData.target_role || null,
        target_companies: formData.target_companies || [],
        skills: formData.skills || [],
        github_url: formData.github_url || null,
        linkedin_url: formData.linkedin_url || null,
      }
    : null

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-1 sm:p-2 lg:p-0">
      <SuccessBanner message={successMessage} onDismiss={() => setSuccessMessage('')} />

      <ProfileHeader
        fullName={user?.full_name || user?.email || 'Your Profile'}
        targetRole={displayProfile?.target_role}
        completionPercentage={displayProfile?.completion_percentage || 0}
      />

      {error && <ErrorMessage message={error} onRetry={() => refetch()} />}

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.35fr]">
        <div className="space-y-6">
          <PersonalInfoCard
            fullName={user?.full_name || user?.email || ''}
            email={user?.email || ''}
            phone={formData.phone}
            onChange={handleFieldChange}
          />

          <EducationCard
            college={formData.college}
            degree={formData.degree}
            branch={formData.branch}
            graduationYear={formData.graduation_year}
            cgpa={formData.cgpa}
            onChange={handleFieldChange}
          />

          <SkillsCard skills={formData.skills} onChange={handleFieldChange} />

          <CareerGoalsCard
            targetRole={formData.target_role}
            targetCompanies={formData.target_companies}
            onChange={handleFieldChange}
          />

          <ProfessionalLinksCard
            githubUrl={formData.github_url}
            linkedinUrl={formData.linkedin_url}
            onChange={handleFieldChange}
          />
        </div>

        <div className="space-y-6">
          <ProfileSidePanel profile={displayProfile} />

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glass backdrop-blur-xl">
            <p className="text-sm text-slate-400">
              Keep your profile current so Resume Analyzer and other modules can personalize your experience.
            </p>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="mt-4 inline-flex items-center rounded-2xl bg-accent px-4 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
