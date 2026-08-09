import api from './api'

export const getInsights = async () => {
  const response = await api.get('/insights')
  return response.data?.data ?? response.data
}

export const askInsightQuestion = async (question) => {
  const response = await api.post('/insights/query', { question })
  return response.data?.data ?? response.data
}
