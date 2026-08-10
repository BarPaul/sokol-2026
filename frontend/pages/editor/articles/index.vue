<template>
  <div class="mx-auto max-w-6xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-900">Статьи</h1>
      <NuxtLink to="/editor/articles/new" class="btn-primary">Создать статью</NuxtLink>
    </div>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row">
      <input v-model="search" class="input-sf flex-1" placeholder="Поиск по названию..." @input="debouncedLoad">
      <select v-model="statusFilter" class="input-sf !w-auto sm:w-48" @change="load">
        <option value="">Все статусы</option>
        <option value="draft">Черновики</option>
        <option value="published">Опубликовано</option>
      </select>
    </div>

    <div class="card-sf overflow-x-auto">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th class="pb-3 pr-4">Название</th>
            <th class="pb-3 pr-4">Категория</th>
            <th class="pb-3 pr-4">Статус</th>
            <th class="pb-3 pr-4">Обновлено</th>
            <th class="pb-3">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in items" :key="a.id" class="border-b border-slate-100 last:border-0">
            <td class="py-3 pr-4 font-medium text-slate-800">{{ a.title }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ a.category }}</td>
            <td class="py-3 pr-4">
              <span class="rounded-full px-2 py-0.5 text-xs" :class="statusClass(a.status)">
                {{ statusName(a.status) }}
              </span>
            </td>
            <td class="py-3 pr-4 text-slate-400">{{ formatDate(a.updated_at) }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <NuxtLink :to="`/editor/articles/${a.id}`" class="text-teal-700 hover:underline">Ред.</NuxtLink>
                <NuxtLink :to="`/editor/articles/${a.id}/coauthors`" class="text-indigo-600 hover:underline">Соавторы</NuxtLink>
                <button class="text-red-600 hover:underline" @click="remove(a)">Удалить</button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0 && !loading">
            <td colspan="5" class="py-10 text-center text-slate-500">Статьи не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Article } from '~/shared/types'

definePageMeta({ layout: 'editor', middleware: 'editor' })

const { request } = useApi()

const items = ref<Article[]>([])
const search = ref('')
const statusFilter = ref('')
const loading = ref(false)

const statusName = (s: string) => (s === 'published' ? 'Опубликовано' : s === 'draft' ? 'Черновик' : 'Архив')
const statusClass = (s: string) =>
  s === 'published' ? 'bg-teal-50 text-teal-700' : 'bg-amber-50 text-amber-700'
const formatDate = (iso: string) => (iso ? new Date(iso).toLocaleDateString('ru-RU') : '')

let timer: ReturnType<typeof setTimeout> | null = null
const debouncedLoad = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 400)
}

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('q', search.value)
    if (statusFilter.value) params.set('status', statusFilter.value)
    const res = await request<{ items: Article[] }>(`/api/editor/articles?${params.toString()}`)
    items.value = res.items
  } finally {
    loading.value = false
  }
}

async function remove(a: Article) {
  if (!confirm(`Удалить статью «${a.title}»?`)) return
  await request(`/api/editor/articles/${a.id}`, { method: 'DELETE' })
  load()
}

onMounted(load)
</script>