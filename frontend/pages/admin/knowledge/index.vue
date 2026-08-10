<template>
  <div class="mx-auto max-w-6xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-900">База знаний AI</h1>
      <NuxtLink to="/admin/knowledge/new" class="btn-primary">Создать документ</NuxtLink>
    </div>

    <div class="mb-4">
      <input v-model="search" class="input-sf max-w-md" placeholder="Поиск по документам..." @input="debouncedLoad">
    </div>

    <div class="card-sf overflow-x-auto">
      <table class="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th class="pb-3 pr-4">Название</th>
            <th class="pb-3 pr-4">Источник</th>
            <th class="pb-3 pr-4">Категория</th>
            <th class="pb-3 pr-4">Статус</th>
            <th class="pb-3 pr-4">Обновлено</th>
            <th class="pb-3">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in docs" :key="d.id" class="border-b border-slate-100 last:border-0">
            <td class="py-3 pr-4 font-medium text-slate-800">{{ d.title }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ d.source }}</td>
            <td class="py-3 pr-4 text-slate-500">{{ d.category }}</td>
            <td class="py-3 pr-4">
              <span class="rounded-full px-2 py-0.5 text-xs" :class="d.is_active ? 'bg-teal-50 text-teal-700' : 'bg-slate-100 text-slate-500'">
                {{ d.is_active ? 'Активен' : 'Отключён' }}
              </span>
            </td>
            <td class="py-3 pr-4 text-slate-400">{{ formatDate(d.updated_at) }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <NuxtLink :to="`/admin/knowledge/${d.id}`" class="text-teal-700 hover:underline">Ред.</NuxtLink>
                <button class="text-red-600 hover:underline" @click="remove(d)">Удалить</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <EmptyState v-if="docs.length === 0" title="Документы не найдены" description="Добавьте материалы для базы знаний." />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeDocument } from '~/shared/types'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { request } = useApi()

const docs = ref<KnowledgeDocument[]>([])
const search = ref('')

const formatDate = (iso: string) => (iso ? new Date(iso).toLocaleDateString('ru-RU') : '')

async function load() {
  const params = search.value ? `?q=${encodeURIComponent(search.value)}` : ''
  docs.value = await request<KnowledgeDocument[]>('/api/admin/knowledge' + params)
}

let timer: ReturnType<typeof setTimeout> | null = null
const debouncedLoad = () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(load, 400)
}

async function remove(d: KnowledgeDocument) {
  if (!confirm(`Удалить документ «${d.title}»?`)) return
  await request(`/api/admin/knowledge/${d.id}`, { method: 'DELETE' })
  load()
}

onMounted(load)
</script>