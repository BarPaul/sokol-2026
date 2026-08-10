export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return
  const token = localStorage.getItem('sf_token')
  if (!token) {
    return navigateTo('/login')
  }
  const role = localStorage.getItem('sf_role')
  if (role !== 'editor' && role !== 'moderator') {
    return navigateTo('/login')
  }
})