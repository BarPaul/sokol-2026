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
        <NuxtLink
          :to="`/articles?category=${encodeURIComponent(article.category || '')}`"
          class="inline-block rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-800 hover:bg-teal-100"
        >
          {{ article.category || 'Без категории' }}
        </NuxtLink>
        <h1 class="mt-4 text-2xl font-bold leading-tight text-slate-900 sm:text-3xl">{{ article.title }}</h1>
        <div class="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-slate-500">
          <time v-if="article.published_at" :datetime="article.published_at">
            <Icon name="heroicons:calendar-days" class="mr-1 inline h-4 w-4" />
            {{ formatDate(article.published_at) }}
          </time>
          <span v-if="article.reading_minutes">
            <Icon name="heroicons:clock" class="mr-1 inline h-4 w-4" />
            ~{{ article.reading_minutes }} мин чтения
          </span>
          <span v-if="article.views !== undefined && article.views !== null">
            <Icon name="heroicons:eye" class="mr-1 inline h-4 w-4" />
            {{ article.views }} {{ pluralViews(article.views) }}
          </span>
        </div>
        <p class="mt-5 text-lg leading-relaxed text-slate-600">{{ article.summary }}</p>

        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="rich-body mt-6" v-html="renderedContent" />

        <div v-if="article.audience" class="mt-8 rounded-lg border-l-4 border-teal-500 bg-teal-50 p-4">
          <h3 class="font-semibold text-teal-900">Кому положено</h3>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div class="mt-1 text-sm leading-relaxed text-teal-800" v-html="article.audience" />
        </div>
        <div v-if="article.documents" class="mt-4 rounded-lg border-l-4 border-sky-500 bg-sky-50 p-4">
          <h3 class="font-semibold text-sky-900">Необходимые документы</h3>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div class="mt-1 text-sm leading-relaxed text-sky-800" v-html="article.documents" />
        </div>
        <div v-if="article.region" class="mt-4 rounded-lg bg-slate-50 p-4">
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

        <div v-if="article.coauthors && article.coauthors.length" class="mt-8 border-t border-slate-100 pt-4">
          <p class="text-sm font-medium text-slate-500">Соавторы:</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="c in article.coauthors" :key="c.id" class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
              {{ c.first_name }} {{ c.last_name }}
            </span>
          </div>
        </div>

        <div class="mt-8 flex items-center gap-3 border-t border-slate-100 pt-5">
          <div class="flex h-11 w-11 items-center justify-center rounded-full bg-teal-700 text-sm font-bold text-white">
            {{ initials(article.author_name) }}
          </div>
          <div>
            <p class="text-sm font-medium text-slate-900">{{ article.author_name }}</p>
            <p class="text-xs text-slate-400">Автор материала</p>
          </div>
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

const pluralViews = (n: number) => {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return 'просмотр'
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 'просмотра'
  return 'просмотров'
}

const initials = (name: string) => {
  const parts = (name || '').trim().split(/\s+/)
  return parts.map((p) => p[0] || '').join('').toUpperCase() || 'А'
}

const renderedContent = computed(() => {
  const raw = article.value?.content || ''
  if (raw.trim() === '') return ''
  // Rich-редактор генерирует HTML; legacy-контент мог храниться как plain/markdown.
  if (/<[a-z][\s\S]*>/i.test(raw)) return raw
  return raw
    .split(/\n+/)
    .map((line) => {
      const m = line.match(/^##\s+(.+)$/)
      if (m) return `<h2 class="mt-6 mb-2 text-xl font-semibold text-slate-900">${m[1]}</h2>`
      return `<p class="mb-3 text-slate-700">${line}</p>`
    })
    .join('\n')
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

<style scoped>
.rich-body :deep(blockquote) {
  margin: 0.75rem 0;
  border-left: 4px solid #0d9488;
  background: #f0fdfa;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  color: #475569;
}
.rich-body :deep(img) {
  max-width: 100%;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
}
.rich-body :deep(a) {
  color: #0f766e;
  text-decoration: underline;
}
.rich-body :deep(h1),
.rich-body :deep(h2),
.rich-body :deep(h3) {
  margin: 1rem 0 0.5rem;
  font-weight: 600;
  color: #0f172a;
}
.rich-body :deep(ul),
.rich-body :deep(ol) {
  padding-left: 1.25rem;
  margin: 0.5rem 0;
}
.rich-body :deep(p) {
  margin-bottom: 0.75rem;
  line-height: 1.7;
  color: #334155;
}
</style>