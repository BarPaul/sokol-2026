<template>
  <div class="container-sf py-8">
    <nav class="mb-4 text-sm text-slate-500">
      <NuxtLink to="/" class="hover:text-teal-700">Главная</NuxtLink>
      <span class="mx-2">/</span>
      <NuxtLink to="/articles" class="hover:text-teal-700">Статьи</NuxtLink>
      <span class="mx-2">/</span>
      <span class="text-slate-700">Статья</span>
    </nav>

    <div v-if="loading" class="py-16 text-center text-sm text-slate-500">Загрузка статьи...</div>
    <div v-else-if="notFound">
      <EmptyState title="Статья не найдена" description="Возможно, материал был удалён или перемещён.">
        <NuxtLink to="/articles" class="btn-primary mt-4">К каталогу</NuxtLink>
      </EmptyState>
    </div>

    <article v-else-if="article" class="grid gap-8 lg:grid-cols-[1fr_320px]">
      <div class="card-sf">
        <span class="inline-block rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-800">
          {{ article.category || 'Без категории' }}
        </span>
        <h1 class="mt-4 text-2xl font-bold text-slate-900 sm:text-3xl">{{ article.title }}</h1>
        <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-slate-400">
          <time v-if="article.updated_at" :datetime="article.updated_at">
            Обновлено: {{ formatDate(article.updated_at) }}
          </time>
          <span v-if="article.author_name">Автор: {{ article.author_name }}</span>
        </div>
        <p class="mt-4 text-lg text-slate-600">{{ article.summary }}</p>

        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="prose max-w-none" v-html="renderedContent" />

        <div v-if="article.region" class="mt-8 rounded-lg bg-slate-50 p-4">
          <h3 class="font-semibold text-slate-900">Регион</h3>
          <p class="mt-1 text-sm text-slate-600">{{ article.region }}</p>
        </div>
        <div v-if="article.official_source" class="mt-4 rounded-lg bg-slate-50 p-4">
          <h3 class="font-semibold text-slate-900">Официальный источник</h3>
          <p class="mt-1 text-sm text-slate-600">{{ article.official_source }}</p>
        </div>
        <div v-if="article.restrictions" class="mt-4 rounded-lg border-l-4 border-amber-400 bg-amber-50 p-4">
          <h3 class="font-semibold text-amber-900">Ограничения</h3>
          <p class="mt-1 text-sm text-amber-800">{{ article.restrictions }}</p>
        </div>
      </div>

      <aside class="flex flex-col gap-6">
        <div class="card-sf bg-slate-900 text-white">
          <h3 class="font-semibold">Вопросы по теме?</h3>
          <p class="mt-2 text-sm text-slate-300">
            Спросите AI-помощника о вашей конкретной ситуации.
          </p>
          <NuxtLink
            :to="`/assistant?q=${encodeURIComponent(article.title)}`"
            class="mt-4 inline-block rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-slate-900 hover:bg-amber-400"
          >
            Спросить AI
          </NuxtLink>
        </div>

        <template v-if="article.related && article.related.length">
          <div>
            <h3 class="mb-3 font-semibold text-slate-900">Похожие статьи</h3>
            <div class="flex flex-col gap-3">
              <NuxtLink
                v-for="r in article.related"
                :key="r.id"
                :to="`/articles/${r.slug}`"
                class="card-sf !py-3 transition hover:border-teal-600"
              >
                <p class="text-sm font-medium text-slate-900">{{ r.title }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ r.category }}</p>
              </NuxtLink>
            </div>
          </div>
        </template>
      </aside>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { Article } from '~/shared/types'

const route = useRoute()
const { request } = useApi()

const article = ref<Article | null>(null)
const loading = ref(true)
const notFound = ref(false)

const formatDate = (iso: string) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

const renderedContent = computed(() => {
  const raw = article.value?.content || ''
  const lines = raw
    .split(/\n+/)
    .map((line) => {
      const m = line.match(/^##\s+(.+)$/)
      if (m) return `<h2 class="mt-6 mb-2 text-xl font-semibold text-slate-900">${m[1]}</h2>`
      return `<p class="mb-3 text-slate-700">${line}</p>`
    })
    .join('\n')
  return lines
})

async function load() {
  loading.value = true
  try {
    const data = await request<Article>(`/api/articles/${route.params.slug}`)
    article.value = data
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>