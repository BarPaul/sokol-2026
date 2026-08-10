<template>
  <div class="mx-auto max-w-6xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-900">Журнал действий</h1>
    </div>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row">
      <input v-model="search" class="input-sf flex-1" placeholder="Поиск по описанию или действию..." @input="debouncedLoad">
      <select v-model="actionFilter" class="input-sf !w-auto sm:w-64" @change="load">
        <option value="">Все действия</option>
        <option v-for="a in actionList" :key="a" :value="a">{{ a }}</option>
      </select>
    </div>

    <div class="card-sf overflow-x-auto">
      <table class="w-full min-w-[720px] text-left text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th class="pb-3 pr-4">Время</th>
            <th class="pb-3 pr-4">Пользователь</th>
            <th class="pb-3 pr-4">Действие</th>
            <th class="pb-3 pr-4">Объект</th>
            <th class="pb-3">Описание</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-b border-slate-100 last:border-0">
            <td class="py-3 pr-4 whitespace-nowrap text-slate-400">{{ formatDate(log.created_at) }}</td>
            <td class="py-3 pr-4 font-medium text-slate-800">{{ log.account_name }}</td>
            <td class="py-3 pr-4">
              <span class="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700">{{ log.action }}</span>
            </td>
            <td class="py-3 pr-4 text-slate-500">{{ log.entity_type }}{{ log.entity_id ? ` #${log.entity_id}` : '' }}</td>
            <td class="py-3 text-slate-600">{{ log.description }}</td>
          </tr>
        </tbody>
      </table>
      <EmptyState v-if="logs.length === 0" title="Записи не найдены" description="Измените фильтры." />
    </div>

    <div v-if="total > logs.length" class="mt-4 flex justify-center gap-2">
      <button class="btn-secondary" :disabled="offset <= 0" @click="prev">Назад</button>
      <button class="btn-secondary" :disabled="offset + limit >= total" @click="next">Вперёд</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LogEntry } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const logs = ref<LogEntry[]>([])
const total = ref(0)
const search = ref('')
const actionFilter = ref('')
const limit = 20
const offset = ref(0)

const formatDate = (iso: string) => (iso ? new Date(iso).toLocaleString('ru-RU') : '')

const actionList = [
  'login',
  'logout',
  'article.created',
  'article.updated',
  'article.deleted',
  'article.published',
  'coauthor.added',
  'coauthor.removed',
  'account.created',
  'account.updated',
  'account.deactivated',
  'ai.settings.updated',
]

async function load() {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset.value) })
  if (search.value) params.set('q', search.value)
  if (actionFilter.value) params.set('action', actionFilter.value)
  const res = await request<{ items: LogEntry[]; total: number }>(`/api/admin/logs?${params.toString()}`)
  logs.value = res.items
  total.value = res.total
}

let timer: ReturnType<typeof setTimeout> | null = null
const debouncedLoad = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 400)
}

const prev = () => {
  offset.value = Math.max(0, offset.value - limit)
  load()
}
const next = () => {
  offset.value += limit
  load()
}

onMounted(load)
</script>