<template>
  <div class="mx-auto max-w-3xl">
    <NuxtLink to="/admin/knowledge" class="mb-4 inline-block text-sm text-teal-700 hover:underline">← К базе знаний</NuxtLink>
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Создание документа</h1>

    <form class="card-sf flex flex-col gap-4" @submit.prevent="submit">
      <div>
        <label class="label-sf">Название *</label>
        <input v-model="form.title" class="input-sf" required>
      </div>
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="label-sf">Источник</label>
          <input v-model="form.source" class="input-sf">
        </div>
        <div>
          <label class="label-sf">Категория</label>
          <input v-model="form.category" class="input-sf">
        </div>
      </div>
      <div>
        <label class="label-sf">Содержание *</label>
        <textarea v-model="form.content" class="input-sf" rows="10" required />
      </div>
      <label class="flex items-center gap-2 text-sm text-slate-700">
        <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-teal-700">
        Активен (используется в базе знаний)
      </label>

      <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

      <div class="flex gap-3">
        <button class="btn-secondary" type="button" @click="router.push('/admin/knowledge')">Отмена</button>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const router = useRouter()
const { request } = useApi()

const form = reactive({ title: '', source: '', category: '', content: '', is_active: true })
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!form.title.trim() || !form.content.trim()) {
    error.value = 'Заполните название и содержание'
    return
  }
  saving.value = true
  try {
    await request('/api/admin/knowledge', { method: 'POST', body: { ...form } })
    router.push('/admin/knowledge')
  } catch (e) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}
</script>