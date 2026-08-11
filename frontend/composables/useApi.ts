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
    const hadAuth = Boolean(t)
    if (t) headers.Authorization = `Bearer ${t}`

    try {
      const res = await $fetch<T>(`${base}${path}`, {
        method: options.method || 'GET',
        body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
        headers,
        credentials: 'include',
        retry: 0,
      })
      return res as T
    } catch (e) {
      const status = (e as { statusCode?: number })?.statusCode
      // Истёкший/недействительный JWT — выбрасываем из аккаунта и на главную.
      if (status === 401 && hadAuth && path !== '/api/auth/refresh') {
        handleSessionExpired()
      }
      throw e
    }
  }

  function handleSessionExpired() {
    setToken(null)
    if (import.meta.client) {
      localStorage.removeItem('sf_role')
      const current = window.location.pathname
      if (current.startsWith('/editor') || current.startsWith('/admin')) {
        navigateTo('/')
      }
    }
  }

  async function refreshSession(): Promise<boolean> {
    // Продлевает токен до 1 часа; на смену раздела вызывается плагином.
    if (!token.value) return false
    try {
      const data = await request<{ access_token: string }>('/api/auth/refresh', { method: 'POST' })
      setToken(data.access_token)
      return true
    } catch {
      handleSessionExpired()
      return false
    }
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
    if (import.meta.client) {
      localStorage.removeItem('sf_role')
      navigateTo('/')
    }
  }

  return { request, login, logout, refreshSession, setToken, token, base }
}