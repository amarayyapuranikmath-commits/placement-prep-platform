// src/hooks/useProfile.js
import { useCallback, useEffect, useState } from 'react'
import { getProfile, updateProfile } from '../services/profileService'

export const useProfile = () => {
  const [profile, setProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  const fetchProfile = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await getProfile()
      setProfile(data)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load profile')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const saveProfile = useCallback(async (payload) => {
    setIsSaving(true)
    setError('')
    try {
      const updated = await updateProfile(payload)
      setProfile(updated)
      return updated
    } catch (err) {
      const message = err.response?.data?.message || 'Failed to update profile'
      setError(message)
      throw new Error(message)
    } finally {
      setIsSaving(false)
    }
  }, [])

  return { profile, isLoading, error, isSaving, saveProfile, refetch: fetchProfile }
}