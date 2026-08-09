import api from '../api'

export const createInterviewSession = async ({ interviewConfig = {}, persona } = {}) => {
  const response = await api.post('/interview/sessions', {
    ...interviewConfig,
    persona,
  })

  return response.data?.data || response.data || {}
}

export const submitInterviewTurn = async ({ sessionId, answer, persona } = {}) => {
  const response = await api.post(`/interview/sessions/${sessionId}/turns`, {
    raw_answer: answer,
    persona,
  })

  return response.data?.data || response.data || {}
}

export const completeInterviewSession = async ({ sessionId } = {}) => {
  const response = await api.post(`/interview/sessions/${sessionId}/complete`)
  return response.data?.data || response.data || {}
}

export const getInterviewReport = async ({ sessionId } = {}) => {
  const response = await api.get(`/interview/sessions/${sessionId}/report`)
  return response.data?.data || response.data || {}
}

export const getInterviewQuestion = async (questionId) => {
  const response = await api.get(`/interview/questions/${questionId}`)
  return response.data?.data || response.data || {}
}
