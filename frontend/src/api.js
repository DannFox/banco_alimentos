import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

export async function downloadBlob(url, suggestedName) {
  const res = await api.get(url, { responseType: 'blob' })
  const blob = new Blob([res.data])
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = suggestedName || 'descarga'
  a.click()
  URL.revokeObjectURL(href)
}
