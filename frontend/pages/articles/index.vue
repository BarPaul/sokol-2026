<template>
  <div class="container-sf py-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Каталог статей</h1>
      <p class="mt-1 text-sm text-slate-500">Материалы по поддержке студенческих семей</p>
    </div>

    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
      <form class="flex flex-1 gap-2" @submit.prevent="applyFilters">
        <input
          v-model="search"
          type="text"
          class="input-sf !w-auto flex-1"
          placeholder="Поиск по статьям..."
        >
        <button class="btn-primary" type="submit">Искать</button>
      </form>
      <select v-model="category" class="input-sf !w-auto sm:w-56" @change="applyFilters">
        <option value="">Все категории</option>
        <option v-for="c in categories" :key="c.name" :value="c.name">{{ c.name }}</option>
      </select>
    </div>

    <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <ArticleCard v-for="a in items" :key="a.id" :article="a" />
    </div>

    <EmptyState
      v-if="!loading && items.length === 0"
      title="Статьи не найдены"
      description="Попробуйте изменить запрос или выбрать другую категорию."
    />

    <div v-if="loading" class="py-10 text-center text-sm text-slate-500">Загрузка статей...</div>

    <div v-if="total > items.length" class="mt-8 flex justify-center gap-2">
      <button class="btn-secondary" :disabled="offset <= 0" @click="prevPage">Назад</button>
      <button class="btn-secondary" :disabled="offset + limit >= total" @click="nextPage">Вперёд</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArticleCard, ArticleListResponse, CategoryItem } from '~/shared/types'

const route = useRoute()
const router = useRouter()
const { request } = useApi()

const items = ref<ArticleCard[]>([])
const categories = ref<CategoryItem[]>([])
const total = ref(0)
const loading = ref(true)
const limit = 12
const offset = ref(0)

const search = ref((route.query.q as string) || '')
const category = ref((route.query.category as string) || '')

async function load() {
  loading.value = true
  try {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset.value) })
    if (search.value) params.set('q', search.value)
    if (category.value) params.set('category', category.value)
    const res = await request<ArticleListResponse>(`/api/articles?${params.toString()}`)
    items.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  offset.value = 0
  const q: Record<string, string> = {}
  if (search.value) q.q = search.value
  if (category.value) q.category = category.value
  router.replace({ query: q })
  load()
}

function prevPage() {
  offset.value = Math.max(0, offset.value - limit)
  load()
}
function nextPage() {
  offset.value += limit
  load()
}

onMounted(async () => {
  load()
  categories.value = await request<CategoryItem[]>('/api/articles/categories')
})
</script>