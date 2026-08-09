// src/services/profileService.js
import api from './api'

export const getProfile = async () => {
  const response = await api.get('/profile')
  return response.data.data ?? response.data
}

export const updateProfile = async (payload) => {
  const response = await api.put('/profile', payload)
  return response.data.data ?? response.data
}