export default defineNuxtPlugin(() => {
  if (!import.meta.client) return

  const { token, refreshSession } = useApi()
  const route = useRoute()

  let lastPath = route.fullPath
  let refreshing = false

  watch(
    () => route.fullPath,
    (path) => {
      if (path === lastPath) return
      const isProtected = path.startsWith('/editor') || path.startsWith('/admin')
      const hadProtection = lastPath.startsWith('/editor') || lastPath.startsWith('/admin')
      lastPath = path
      if (token.value && isProtected && !refreshing) {
        refreshing = true
        refreshSession().finally(() => {
          refreshing = false
        })
      } else if (hadProtection && !isProtected) {
        // Редактор/админ перешёл на публичную часть: токен будет продлён снова при возврате.
      }
    },
  )
})