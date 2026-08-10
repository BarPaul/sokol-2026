interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'
  body?: unknown
  token?: string | null
}

export function useApi() {
  const config = useRuntimeConfig()
  const base = (config.public as { apiBase: string }).apiBase
  const token = useState<string | null>('auth-token', () => (import.meta.client ? localStorage.getItem('sf_token') : null))

  const setToken = (t: string | null) => {
    token.value = t
    if (import.meta.client) {
      if (t) localStorage.setItem('sf_token', t)
      else localStorage.removeItem('sf_token')
    }
  }

  async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    const t = options.token ?? token.value
    if (t) headers.Authorization = `Bearer ${t}`

    const res = await $fetch<T>(`${base}${path}`, {
      method: options.method || 'GET',
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      headers,
      retry: 0,
    })

    return res as T
  }

  async function login(email: string, password: string): Promise<string> {
    const data = await request<{ access_token: string }>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    setToken(data.access_token)
    if (import.meta.client) {
      try {
        const payload = JSON.parse(atob(data.access_token.split('.')[1]))
        localStorage.setItem('sf_role', payload.role || '')
      } catch {
        /* ignore */
      }
    }
    return data.access_token
  }

  function logout() {
    setToken(null)
    if (import.meta.client) localStorage.removeItem('sf_role')
  }

  return { request, login, logout, setToken, token, base }
}