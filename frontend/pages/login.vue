<template>
  <div class="container-sf flex min-h-[60vh] items-center justify-center py-12">
    <div class="card-sf w-full max-w-md">
      <h1 class="mb-1 text-2xl font-bold text-slate-900">Вход</h1>
      <p class="mb-6 text-sm text-slate-500">Доступ для редакторов и администраторов</p>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div>
          <label class="label-sf" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="input-sf" placeholder="you@example.ru" required>
        </div>
        <div>
          <label class="label-sf" for="password">Пароль</label>
          <input id="password" v-model="password" type="password" class="input-sf" placeholder="••••••••" required>
        </div>

        <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

        <button class="btn-primary !py-2.5" type="submit" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <div class="mt-4 text-center">
        <NuxtLink to="/password-recovery" class="text-sm text-teal-700 hover:text-teal-800">
          Забыли пароль?
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const { login } = useApi()
const router = useRouter()

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    const role = localStorage.getItem('sf_role')
    if (role === 'moderator') {
      router.push('/admin')
    } else {
      router.push('/editor')
    }
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Не удалось войти. Проверьте данные.'
  } finally {
    loading.value = false
  }
}
</script>