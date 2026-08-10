<template>
  <div class="container-sf py-8">
    <h1 class="mb-6 text-2xl font-bold text-slate-900">Поиск по статьям</h1>

    <form class="mb-8 flex gap-2" @submit.prevent="doSearch">
      <input
        v-model="query"
        type="text"
        class="input-sf flex-1"
        placeholder="Что вас интересует?"
      >
      <button class="btn-primary" type="submit">Искать</button>
    </form>

    <template v-if="searched">
      <p class="mb-4 text-sm text-slate-500">
        По запросу «{{ lastQuery }}» найдено результатов: {{ total }}
      </p>
      <div v-if="items.length" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <ArticleCard v-for="a in items" :key="a.id" :article="a" />
      </div>
      <EmptyState
        v-else
        title="Ничего не найдено"
        description="Попробуйте изменить формулировку или обратиться к AI-помощнику."
      >
        <NuxtLink to="/assistant" class="btn-primary mt-4">Спросить AI-помощника</NuxtLink>
      </EmptyState>
    </template>

    <EmptyState
      v-if="!searched"
      title="Ищете что-то конкретное?"
      description="Введите ключевые слова — например «пособие», «общежитие», «стипендия»."
    />
  </div>
</template>

<script setup lang="ts">
import type { ArticleCard } from '~/shared/types'

const route = useRoute()
const { request } = useApi()

const query = ref((route.query.q as string) || '')
const items = ref<ArticleCard[]>([])
const total = ref(0)
const searched = ref(false)
const lastQuery = ref('')

async function doSearch() {
  const q = query.value.trim()
  if (!q) return
  lastQuery.value = q
  const res = await request<{ items: ArticleCard[]; total: number }>(`/api/articles/search?q=${encodeURIComponent(q)}`)
  items.value = res.items
  total.value = res.total
  searched.value = true
}

onMounted(() => {
  if (route.query.q) doSearch()
})
</script>