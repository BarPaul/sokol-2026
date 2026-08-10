<template>
  <div class="mx-auto max-w-6xl">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Дашборд администратора</h1>

    <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="card-sf">
        <p class="text-sm text-slate-500">Редакторов</p>
        <p class="mt-1 text-3xl font-bold text-slate-900">{{ stats.editors }}</p>
      </div>
      <div class="card-sf">
        <p class="text-sm text-slate-500">Всего статей</p>
        <p class="mt-1 text-3xl font-bold text-slate-900">{{ stats.totalArticles }}</p>
      </div>
      <div class="card-sf">
        <p class="text-sm text-slate-500">Опубликовано</p>
        <p class="mt-1 text-3xl font-bold text-teal-700">{{ stats.published }}</p>
      </div>
      <div class="card-sf">
        <p class="text-sm text-slate-500">Черновики</p>
        <p class="mt-1 text-3xl font-bold text-amber-600">{{ stats.drafts }}</p>
      </div>
    </div>

    <div class="card-sf">
      <div class="flex items-center justify-between">
        <p class="font-semibold text-slate-900">Последняя активность</p>
        <NuxtLink to="/admin/logs" class="text-sm text-teal-700 hover:underline">Все →</NuxtLink>
      </div>
      <div class="mt-4 flex flex-col divide-y divide-slate-100">
        <div v-for="log in logs" :key="log.id" class="flex items-center justify-between py-3">
          <div>
            <p class="text-sm font-medium text-slate-800">{{ log.account_name }} — {{ log.action }}</p>
            <p class="text-xs text-slate-400">{{ log.description }}</p>
          </div>
          <time class="text-xs text-slate-400">{{ formatDate(log.created_at) }}</time>
        </div>
        <p v-if="logs.length === 0" class="py-6 text-center text-sm text-slate-500">Активности пока нет</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Article, EditorAccount, LogEntry } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const stats = ref({ editors: 0, totalArticles: 0, published: 0, drafts: 0 })
const logs = ref<LogEntry[]>([])

const formatDate = (iso: string) => (iso ? new Date(iso).toLocaleString('ru-RU') : '')

onMounted(async () => {
  const [editors, editorRes, logsRes] = await Promise.all([
    request<EditorAccount[]>('/api/admin/editors'),
    request<{ items: Article[]; total: number }>('/api/editor/articles'),
    request<{ items: LogEntry[]; total: number }>('/api/admin/logs?limit=6'),
  ])
  stats.value = {
    editors: editors.length,
    totalArticles: editorRes.total,
    published: editorRes.items.filter(a => a.status === 'published').length,
    drafts: editorRes.items.filter(a => a.status === 'draft').length,
  }
  logs.value = logsRes.items
})
</script>