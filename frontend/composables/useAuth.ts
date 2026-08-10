import type { Account } from '~/shared/types'

interface AuthState {
  account: Account | null
  token: string | null
}

export function useAuth() {
  const state = useState<AuthState>('auth', () => ({
    account: null,
    token: null,
  }))

  const { request } = useApi()

  async function fetchMe() {
    try {
      const account = await request<Account>('/api/auth/me')
      state.value.account = account
      return account
    } catch {
      state.value.account = null
      return null
    }
  }

  const isAuthenticated = computed(() => !!useApi().token.value)
  const isEditor = computed(() => state.value.account?.role === 'editor')
  const isModerator = computed(() => state.value.account?.role === 'moderator')

  return { state, fetchMe, isAuthenticated, isEditor, isModerator }
}