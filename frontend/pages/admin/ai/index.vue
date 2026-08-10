<template>
  <div class="mx-auto max-w-3xl">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Настройки AI-помощника</h1>

    <form class="card-sf flex flex-col gap-5" @submit.prevent="save">
      <div>
        <label class="label-sf">Системный промпт</label>
        <textarea v-model="form.system_prompt" class="input-sf" rows="8" />
        <p class="mt-1 text-xs text-slate-400">Определяет роль и правила ответа ассистента. Хранится на сервере.</p>
      </div>
      <div class="grid gap-5 sm:grid-cols-3">
        <div>
          <label class="label-sf">Модель</label>
          <input v-model="form.model" class="input-sf">
        </div>
        <div>
          <label class="label-sf">Temperature</label>
          <input v-model.number="form.temperature" type="number" step="0.1" min="0" max="1" class="input-sf">
        </div>
        <div>
          <label class="label-sf">Max tokens</label>
          <input v-model.number="form.max_tokens" type="number" min="1" class="input-sf">
        </div>
      </div>
      <label class="flex items-center gap-2 text-sm text-slate-700">
        <input v-model="form.knowledge_enabled" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-teal-700">
        Использовать базу знаний
      </label>

      <p v-if="message" class="rounded-lg px-3 py-2 text-sm" :class="error ? 'bg-red-50 text-red-700' : 'bg-teal-50 text-teal-800'">
        {{ message }}
      </p>

      <div class="flex gap-3">
        <button class="btn-primary" type="submit" :disabled="saving">Сохранить настройки</button>
        <button class="btn-secondary" type="button" :disabled="reindexing" @click="reindex">
          {{ reindexing ? 'Индексация...' : 'Переиндексировать базу знаний' }}
        </button>
      </div>
    </form>

    <div class="card-sf mt-6">
      <p class="text-sm text-slate-500">
        Проверка интеграции: <span v-if="status !== null" :class="status ? 'text-teal-700' : 'text-red-600'">
          {{ status ? 'OpenCode API настроен и доступен' : 'API-ключ или endpoint не настроен' }}
        </span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AISettings } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const form = reactive({
  system_prompt: '',
  model: '',
  temperature: 0.2,
  max_tokens: 1024,
  knowledge_enabled: true,
})
const saving = ref(false)
const reindexing = ref(false)
const message = ref('')
const error = ref(false)
const status = ref<boolean | null>(null)

async function load() {
  const s = await request<AISettings>('/api/admin/ai/settings')
  Object.assign(form, {
    system_prompt: s.system_prompt,
    model: s.model,
    temperature: s.temperature,
    max_tokens: s.max_tokens,
    knowledge_enabled: s.knowledge_enabled,
  })
}

async function save() {
  saving.value = true
  message.value = ''
  error.value = false
  try {
    await request('/api/admin/ai/settings', { method: 'PATCH', body: { ...form } })
    message.value = 'Настройки сохранены'
  } catch {
    error.value = true
    message.value = 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

async function reindex() {
  reindexing.value = true
  try {
    const res = await request<{ documents: number }>('/api/admin/knowledge/reindex', { method: 'POST' })
    message.value = `База знаний переиндексирована: ${res.documents} документов`
    error.value = false
  } catch {
    error.value = true
    message.value = 'Ошибка переиндексации'
  } finally {
    reindexing.value = false
  }
}

onMounted(load)
</script>