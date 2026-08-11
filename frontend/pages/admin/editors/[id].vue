<template>
  <div class="mx-auto max-w-3xl">
    <NuxtLink to="/admin/editors" class="mb-4 inline-block text-sm text-teal-700 hover:underline">← К редакторам</NuxtLink>

    <div v-if="loading" class="py-16 text-center text-sm text-slate-500">Загрузка...</div>

    <template v-else-if="editor">
      <div class="card-sf mb-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-slate-900">{{ editor.first_name }} {{ editor.last_name }}</h1>
            <p class="mt-1 text-sm text-slate-500">{{ editor.email }}</p>
          </div>
          <div class="flex gap-2">
            <span class="rounded-full px-3 py-1 text-xs" :class="editor.role === 'moderator' ? 'bg-indigo-50 text-indigo-700' : 'bg-teal-50 text-teal-700'">
              {{ editor.role === 'moderator' ? 'Администратор' : 'Редактор' }}
            </span>
            <span class="rounded-full px-3 py-1 text-xs" :class="editor.status === 'active' ? 'bg-teal-50 text-teal-700' : 'bg-red-50 text-red-600'">
              {{ editor.status === 'active' ? 'Активен' : 'Деактивирован' }}
            </span>
          </div>
        </div>
      </div>

      <div class="mb-6 grid gap-4 sm:grid-cols-3">
        <div class="card-sf">
          <p class="text-sm text-slate-500">Статей (автор)</p>
          <p class="mt-1 text-2xl font-bold text-slate-900">{{ editor.articles_count ?? 0 }}</p>
        </div>
        <div class="card-sf">
          <p class="text-sm text-slate-500">Создан</p>
          <p class="mt-1 text-sm font-medium text-slate-800">{{ formatDate(editor.created_at) }}</p>
        </div>
        <div class="card-sf">
          <p class="text-sm text-slate-500">Последний вход</p>
          <p class="mt-1 text-sm font-medium text-slate-800">{{ editor.last_login_at ? formatDate(editor.last_login_at) : '—' }}</p>
        </div>
      </div>

      <div class="card-sf">
        <p class="mb-3 font-semibold text-slate-900">Действия</p>
        <div class="flex flex-wrap gap-2">
          <button v-if="editor.status === 'active'" class="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100" @click="toggle">
            Деактивировать
          </button>
          <button v-else class="rounded-lg border border-teal-200 bg-teal-50 px-4 py-2 text-sm font-medium text-teal-700 hover:bg-teal-100" @click="toggle">
            Активировать
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { EditorAccount } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const { request } = useApi()

const editorId = Number(route.params.id)
const editor = ref<EditorAccount | null>(null)
const loading = ref(true)

const formatDate = (iso?: string) => (iso ? new Date(iso).toLocaleDateString('ru-RU') : '—')

async function load() {
  loading.value = true
  try {
    editor.value = await request<EditorAccount>(`/api/admin/editors/${editorId}`)
  } finally {
    loading.value = false
  }
}

async function toggle() {
  if (!editor.value) return
  const status = editor.value.status === 'active' ? 'inactive' : 'active'
  editor.value = await request<EditorAccount>(`/api/admin/editors/${editorId}`, {
    method: 'PATCH',
    body: { status },
  })
}

onMounted(load)
</script>