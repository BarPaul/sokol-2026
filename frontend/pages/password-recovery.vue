<template>
  <div class="container-sf flex min-h-[60vh] items-center justify-center py-12">
    <div class="card-sf w-full max-w-md">
      <h1 class="mb-1 text-2xl font-bold text-slate-900">Восстановление пароля</h1>
      <p class="mb-6 text-sm text-slate-500">Укажите email — мы пришлём инструкции</p>

      <form class="flex flex-col gap-4" @submit.prevent="submit">
        <div>
          <label class="label-sf" for="recovery-email">Email</label>
          <input id="recovery-email" v-model="email" type="email" class="input-sf" placeholder="you@example.ru" required>
        </div>

        <p v-if="message" class="rounded-lg bg-teal-50 px-3 py-2 text-sm text-teal-800">{{ message }}</p>

        <button class="btn-primary !py-2.5" type="submit" :disabled="loading">
          {{ loading ? 'Отправка...' : 'Отправить инструкции' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
const email = ref('')
const message = ref('')
const loading = ref(false)
const { request } = useApi()

async function submit() {
  if (!email.value) return
  loading.value = true
  message.value = ''
  try {
    const res = await request<{ message: string }>('/api/auth/password-recovery', {
      method: 'POST',
      body: { email: email.value },
    })
    message.value = res.message
  } catch {
    message.value = 'Запрос обработан.'
  } finally {
    loading.value = false
  }
}
</script>