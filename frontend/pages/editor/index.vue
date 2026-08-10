<template>
  <div class="mx-auto max-w-6xl">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Дашборд</h1>

    <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div class="card-sf">
        <p class="text-sm text-slate-500">Всего материалов</p>
        <p class="mt-1 text-3xl font-bold text-slate-900">{{ stats.total }}</p>
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

    <div class="card-sf mb-8">
      <div class="flex items-center justify-between">
        <p class="font-semibold text-slate-900">Последние материалы</p>
        <NuxtLink to="/editor/articles" class="text-sm text-teal-700 hover:text-teal-800">Все →</NuxtLink>
      </div>
      <div class="mt-4 flex flex-col divide-y divide-slate-100">
        <NuxtLink
          v-for="a in recent"
          :key="a.id"
          :to="`/editor/articles/${a.id}`"
          class="flex items-center justify-between py-3 hover:bg-slate-50"
        >
          <div class="flex items-center gap-3">
            <span class="rounded-full text-xs" :class="statusClass(a.status)">{{ statusName(a.status) }}</span>
            <p class="text-sm font-medium text-slate-800">{{ a.title }}</p>
          </div>
          <time class="text-xs text-slate-400">{{ formatDate(a.updated_at) }}</time>
        </NuxtLink>
        <EmptyState v-if="recent.length === 0" title="Пока нет материалов" description="Создайте первую статью." />
      </div>
    </div>

    <div class="flex gap-3">
      <NuxtLink to="/editor/articles/new" class="btn-primary">Создать статью</NuxtLink>
      <NuxtLink to="/editor/articles" class="btn-secondary">К списку статей</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Article } from '~/shared/types'

definePageMeta({ layout: 'editor', middleware: 'editor' })

const { request } = useApi()

const articles = ref<Article[]>([])
const recent = computed(() => articles.value.slice(0, 6))
const stats = computed(() => ({
  total: articles.value.length,
  published: articles.value.filter(a => a.status === 'published').length,
  drafts: articles.value.filter(a => a.status === 'draft').length,
}))

const statusName = (s: string) => (s === 'published' ? 'Опубликовано' : s === 'draft' ? 'Черновик' : 'Архив')
const statusClass = (s: string) =>
  s === 'published' ? 'bg-teal-50 px-2 py-0.5 text-teal-700' : 'bg-amber-50 px-2 py-0.5 text-amber-700'
const formatDate = (iso: string) => (iso ? new Date(iso).toLocaleDateString('ru-RU') : '')

onMounted(async () => {
  const res = await request<{ items: Article[]; total: number }>('/api/editor/articles')
  articles.value = res.items
})
</script>