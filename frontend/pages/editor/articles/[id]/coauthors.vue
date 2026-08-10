<template>
  <div class="mx-auto max-w-3xl">
    <NuxtLink to="/editor/articles" class="mb-4 inline-block text-sm text-teal-700 hover:underline">← К статьям</NuxtLink>
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Соавторы статьи</h1>

    <div class="card-sf mb-6">
      <p class="mb-1 font-semibold text-slate-900">{{ article?.title }}</p>
      <p class="text-sm text-slate-500">Основной автор: {{ article?.author_name }}</p>
    </div>

    <div class="card-sf mb-6">
      <p class="mb-3 font-semibold text-slate-900">Текущие соавторы</p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="c in coauthors"
          :key="c.id"
          class="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700"
        >
          {{ c.first_name }} {{ c.last_name }} ({{ c.email }})
          <button class="text-red-500 hover:text-red-700" title="Удалить" @click="remove(c.id)">×</button>
        </span>
        <span v-if="coauthors.length === 0" class="text-sm text-slate-400">Соавторов пока нет</span>
      </div>
    </div>

    <div class="card-sf">
      <p class="mb-3 font-semibold text-slate-900">Добавить соавтора</p>
      <div class="flex flex-col gap-2 sm:flex-row">
        <input
          v-model="search"
          class="input-sf"
          placeholder="Поиск по имени или email..."
          @input="searchEditors"
        >
      </div>
      <div class="mt-4 flex flex-col divide-y divide-slate-100">
        <div
          v-for="e in editors"
          :key="e.id"
          class="flex items-center justify-between py-2.5"
        >
          <div>
            <p class="text-sm font-medium text-slate-800">{{ e.first_name }} {{ e.last_name }}</p>
            <p class="text-xs text-slate-400">{{ e.email }}</p>
          </div>
          <button class="btn-primary !py-1 !text-xs" @click="add(e.id)">Добавить</button>
        </div>
        <EmptyState v-if="editors.length === 0" title="Редакторы не найдены" description="Начните вводить имя или email." />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Article, EditorAccount } from '~/shared/types'

definePageMeta({ layout: 'editor', middleware: 'editor' })

const route = useRoute()
const { request } = useApi()

const articleId = Number(route.params.id)
const article = ref<Article | null>(null)
const coauthors = ref<Article['coauthors']>([])
const editors = ref<EditorAccount[]>([])
const search = ref('')

async function loadArticle() {
  const a = await request<Article>(`/api/editor/articles/${articleId}`)
  article.value = a
  coauthors.value = a.coauthors || []
}

async function searchEditors() {
  const params = search.value ? `?q=${encodeURIComponent(search.value)}` : ''
  const res = await request<EditorAccount[]>('/api/admin/editors' + params)
  editors.value = res.filter(e => !coauthors.value.some(c => c.id === e.id) && e.id !== article.value?.author_id)
}

async function add(id: number) {
  await request<Article>(`/api/editor/articles/${articleId}/coauthors`, { method: 'POST', body: { account_id: id } })
  await loadArticle()
  await searchEditors()
}

async function remove(id: number) {
  await request<Article>(`/api/editor/articles/${articleId}/coauthors/${id}`, { method: 'DELETE' })
  await loadArticle()
  await searchEditors()
}

onMounted(async () => {
  await loadArticle()
  await searchEditors()
})
</script>