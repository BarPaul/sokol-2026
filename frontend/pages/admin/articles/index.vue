<template>
  <div class="mx-auto max-w-6xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Статьи</h1>
      <p class="mt-1 text-sm text-slate-500">Поиск по названию, описанию, содержанию и категории.</p>
    </div>

    <div class="mb-4 flex flex-col gap-3 sm:flex-row">
      <input v-model="search" class="input-sf flex-1" placeholder="Поиск по статьям..." @input="debouncedLoad">
      <select v-model="statusFilter" class="input-sf !w-auto sm:w-48" @change="load">
        <option value="">Все статусы</option>
        <option value="draft">Черновики</option>
        <option value="published">Опубликовано</option>
        <option value="archived">Снято с публикации</option>
      </select>
    </div>

    <div class="card-sf overflow-x-auto">
      <table class="w-full min-w-[720px] text-left text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th class="pb-3 pr-4">Название</th>
            <th class="pb-3 pr-4">Категория</th>
            <th class="pb-3 pr-4">Статус</th>
            <th class="pb-3 pr-4">Автор</th>
            <th class="pb-3 pr-4">Просмотры</th>
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
            <td class="py-3 pr-4 text-slate-500">{{ a.author_name }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ a.views ?? 0 }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <NuxtLink :to="`/articles/${a.slug}`" class="text-teal-700 hover:underline">Открыть</NuxtLink>
                <button v-if="a.status === 'published'" class="text-amber-600 hover:underline" @click="unpublish(a)">
                  Снять
                </button>
                <button v-if="a.status !== 'published'" class="text-indigo-600 hover:underline" @click="publish(a)">
                  Опубликовать
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0 && !loading">
            <td colspan="6" class="py-10 text-center text-slate-500">Статьи не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Article } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const items = ref<Article[]>([])
const search = ref('')
const statusFilter = ref('')
const loading = ref(false)

const statusName = (s: string) => (s === 'published' ? 'Опубликовано' : s === 'draft' ? 'Черновик' : 'Архив')
const statusClass = (s: string) =>
  s === 'published' ? 'bg-teal-50 text-teal-700' : s === 'draft' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'

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
    const res = await request<{ items: Article[] }>(`/api/admin/articles?${params.toString()}`)
    items.value = res.items
  } finally {
    loading.value = false
  }
}

async function unpublish(a: Article) {
  await request<Article>(`/api/editor/articles/${a.id}/unpublish`, { method: 'POST' })
  load()
}

async function publish(a: Article) {
  await request<Article>(`/api/editor/articles/${a.id}/publish`, { method: 'POST' })
  load()
}

onMounted(load)
</script>