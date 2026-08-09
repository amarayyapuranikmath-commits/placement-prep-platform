import api from './api'

export const createAptitudeSession = async (payload) => {
  const response = await api.post('/aptitude/sessions', payload)
  return response.data?.data
}

export const getAptitudeSession = async (sessionId) => {
  const response = await api.get(`/aptitude/sessions/${sessionId}`)
  return response.data?.data
}

export const saveAptitudeAnswer = async (sessionId, questionId, payload) => {
  const response = await api.post(`/aptitude/sessions/${sessionId}/answers`, {
    question_id: questionId,
    ...payload,
  })
  return response.data?.data
}

export const clearAptitudeAnswer = async (sessionId, questionId) => {
  const response = await api.delete(`/aptitude/sessions/${sessionId}/answers/${questionId}`)
  return response.data?.data
}

export const submitAptitudeSession = async (sessionId) => {
  const response = await api.post(`/aptitude/sessions/${sessionId}/submit`)
  return response.data?.data
}

export const getAptitudeReview = async (sessionId) => {
  const response = await api.get(`/aptitude/sessions/${sessionId}/review`)
  return response.data?.data
}

export const getAptitudeHistory = async () => {
  const response = await api.get('/aptitude/history')
  return response.data?.data?.history || []
}

export const getAptitudeResult = async (sessionId) => {
  const response = await api.get(`/aptitude/sessions/${sessionId}/result`)
  return response.data?.data
}
