<template>
  <div class="mx-auto max-w-md">
    <NuxtLink to="/admin/editors" class="mb-4 inline-block text-sm text-teal-700 hover:underline">← К редакторам</NuxtLink>
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Создание редактора</h1>

    <form class="card-sf flex flex-col gap-4" @submit.prevent="submit">
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="label-sf">Имя *</label>
          <input v-model="form.first_name" class="input-sf" required>
        </div>
        <div>
          <label class="label-sf">Фамилия *</label>
          <input v-model="form.last_name" class="input-sf" required>
        </div>
      </div>
      <div>
        <label class="label-sf">Email *</label>
        <input v-model="form.email" type="email" class="input-sf" required>
      </div>
      <div>
        <label class="label-sf">Пароль *</label>
        <input v-model="form.password" type="password" class="input-sf" minlength="6" required>
      </div>

      <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

      <div class="flex gap-3">
        <button class="btn-secondary" type="button" @click="router.push('/admin/editors')">Отмена</button>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Создание...' : 'Создать редактора' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { editorCreateSchema } from '~/shared/schemas'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const router = useRouter()
const { request } = useApi()

const form = reactive({ first_name: '', last_name: '', email: '', password: '', role: 'editor' })
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  const res = editorCreateSchema.safeParse({ ...form })
  if (!res.success) {
    error.value = res.error.errors[0]?.message || 'Проверьте данные'
    return
  }
  saving.value = true
  try {
    await request('/api/admin/editors', { method: 'POST', body: { ...form } })
    router.push('/admin/editors')
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка создания'
  } finally {
    saving.value = false
  }
}
</script>