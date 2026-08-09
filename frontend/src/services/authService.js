import api from './api'

export const login = async ({ email, password }) => {
  const payload = new URLSearchParams()
  payload.append('username', email)
  payload.append('password', password)
  payload.append('grant_type', 'password')

  const response = await api.post('/auth/login', payload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })

  return response.data.data ?? response.data
}

export const register = async (payload) => {
  const response = await api.post('/auth/register', payload)
  return response.data.data ?? response.data
}

export const fetchCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data.data ?? response.data
}
