<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-b from-teal-700 to-teal-800 py-16 text-white">
      <div class="container-sf">
        <h1 class="max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">
          Информация о льготах и поддержке студенческих семей
        </h1>
        <p class="mt-4 max-w-2xl text-teal-50">
          Структурированные статьи и AI-помощник, который поможет разобраться, какие меры поддержки вам положены.
        </p>
        <div class="mt-8 max-w-xl">
          <form class="flex gap-2" @submit.prevent="goSearch">
            <input
              v-model="query"
              type="text"
              class="flex-1 rounded-lg border-0 bg-white px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-400"
              placeholder="Например: ежемесячное пособие"
            >
            <button class="rounded-lg bg-amber-500 px-5 py-3 font-medium text-slate-900 hover:bg-amber-400">
              Найти
            </button>
          </form>
        </div>
      </div>
    </section>

    <!-- Categories / topics -->
    <section class="container-sf py-12">
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-xl font-semibold text-slate-900">Темы</h2>
        <NuxtLink to="/articles" class="text-sm font-medium text-teal-700 hover:text-teal-800">Все статьи →</NuxtLink>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="cat in categories"
          :key="cat.name"
          :to="`/articles?category=${encodeURIComponent(cat.name)}`"
          class="card-sf transition hover:border-teal-600 hover:shadow-md"
        >
          <div class="flex items-center justify-between">
            <p class="font-medium text-slate-900">{{ cat.name }}</p>
            <span class="text-sm text-slate-500">{{ cat.count }}</span>
          </div>
        </NuxtLink>
        <div
          v-if="loading && categories.length === 0"
          class="card-sf text-sm text-slate-500"
        >
          Загрузка тем...
        </div>
      </div>
    </section>

    <!-- Latest articles -->
    <section class="container-sf pb-12">
      <h2 class="mb-6 text-xl font-semibold text-slate-900">Последние статьи</h2>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <ArticleCard
          v-for="a in articles"
          :key="a.id"
          :article="a"
        />
        <div v-if="loading && articles.length === 0" class="col-span-full text-sm text-slate-500">Загрузка...</div>
      </div>
    </section>

    <!-- AI CTA -->
    <section class="container-sf pb-12">
      <div class="rounded-2xl bg-slate-900 p-8 text-white sm:p-10">
        <div class="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-2xl font-bold">Не нашли ответ? Спросите AI-помощника</h2>
            <p class="mt-2 max-w-xl text-slate-300">
              Опишите свою ситуацию — ассистент подберёт релевантные материалы и подскажет, куда обратиться.
            </p>
          </div>
          <NuxtLink to="/assistant" class="btn-primary !bg-amber-500 !text-slate-900 hover:!bg-amber-400">
            Открыть AI-помощника
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { ArticleCard, CategoryItem } from '~/shared/types'

const query = ref('')
const articles = ref<ArticleCard[]>([])
const categories = ref<CategoryItem[]>([])
const loading = ref(true)
const { request } = useApi()

const goSearch = () => {
  if (query.value.trim()) {
    navigateTo(`/search?q=${encodeURIComponent(query.value.trim())}`)
  }
}

onMounted(async () => {
  try {
    const [artRes, catRes] = await Promise.all([
      request<{ items: ArticleCard[] }>('/api/articles?limit=6'),
      request<CategoryItem[]>('/api/articles/categories'),
    ])
    articles.value = artRes.items
    categories.value = catRes
  } finally {
    loading.value = false
  }
})
</script>